import pandas as pd
from typing import List
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db.models.query import QuerySet
from pandas.core.interchange.dataframe_protocol import DataFrame
from apps.common.models import *
from logics.service import Service
from .position_base import PositionBase
from django.db.models import (
    F,Case, When, Value, IntegerField,
    Sum, Max,Min, Q, BooleanField,Subquery, OuterRef)


class OpenPosition(PositionBase):

    def __init__(self, service: Service):
        super().__init__(service)

    def Position(self, portfolio: Portfolio) -> (pd.DataFrame, date) or (None, None):

        holdings = Holding.objects.filter(portfolio=portfolio)
        if len(holdings) <= 0:
            return None,None

        # Step 0. Convert holdings to DataFrame
        final_df = pd.DataFrame(list(holdings.values()))
        final_df.rename(columns={'symbol_id': 'symbol'}, inplace=True)

        # Step 1. Attach data
        # Step 1.a Merge the initial & current stop order into holdings_df
        final_df = pd.merge(final_df, self.get_holding_initial_stop(), on='holding_id', how='inner')
        final_df = pd.merge(final_df, self.get_holding_current_stop(), on='holding_id', how='left')
        # Step 1.b Attach Trade info
        final_df = pd.merge(final_df, self.get_trading_info(final_df), on='trade_id', how='left')
        # Step 1.c Attach Market Benchmark
        final_df = pd.merge(final_df, self.get_market_benchmark(final_df['symbol'].unique()), on='symbol', how='left')
        # Step 1.d Attach Open Position & Initial Position
        final_df = pd.merge(final_df, self.get_current_position(holdings), left_on='holding_id', right_on='holding_id', how='inner').fillna(0)
        final_df = pd.merge(final_df, self.get_init_position(final_df['init_tran_id'].tolist()), on='holding_id', how='left')
        # Step 1.e Attach today_delta
        final_df, max_date = self.attach_today_delta(final_df)

        # Step 2. Calculate
        # Step 2.a Calculate market value
        self.calc_market_value_trand(final_df)
        # Step 2.b Calculate Risk vs Margin
        self.calc_risk_vs_gain(final_df)
        # Step 2.c Calculate goal
        self.calc_goal(final_df)

        # Last Step: Sort by trade_phase in descending order
        final_df.sort_values(by='trade_phase', ascending=False, inplace=True)

        return final_df, max_date

    def summary(self, portfolio:Portfolio, final_df: pd.DataFrame) -> dict:
        ##### Calculate the summary tab ##############
        summary = {
            'holding_symbols': '',
            'mv': {
                'value': 0,
                'change': 0,
                'percent': 0,
            },
            'assets': {
                'value': 0,
                'change': 0,
                'percent': 0,
            },
            'unrealized': {
                'gain': 0,
                'risk': 0,
                'dist': 0,
            },
            'water': {
                'above': 0,
                'below': 0,
                'dist': 0,
            }
        }

        # Part 1. holding_symbols
        symbols = [item.symbol.symbol for item in Holding.objects.filter(portfolio=portfolio)]
        summary['holding_symbols'] = '|'.join(symbols)

        # Part 2. market value
        summary['mv']['value'] = final_df['market'].sum()
        mv_bk = final_df['bk_market'].sum() - final_df['delta'].sum()
        summary['mv']['change'] = summary['mv']['value'] - mv_bk
        summary['mv']['percent'] = summary['mv']['change'] / mv_bk * 100

        # Part 4. gain, risk, and dist
        summary['unrealized']['gain'] = final_df['gain'].sum()
        summary['unrealized']['risk'] = final_df['risk'].sum()
        summary['unrealized']['dist'] = final_df['dist'].sum()

        # Part 5. water above and below
        summary['water']['above'] = final_df[final_df['risk'] > 0]['risk'].sum()
        summary['water']['below'] = final_df[final_df['risk'] < 0]['risk'].sum()
        summary['water']['dist'] = summary['water']['above']  + summary['water']['below']

        return summary

    def get_holding_initial_stop(self) -> pd.DataFrame:

        # Subquery to get the maximum holding_sell_order_id for each holding_id
        max_id_subquery = Order.objects.filter(
            holding_id=OuterRef('holding_id'),
            order_style=2,
            action=1
        ).order_by('-order_id').values('order_id')[:1]

        # Query to get initial sell orders (action=1) for each holding_id based on the subquery
        initial_sell_orders = Order.objects.filter(
            order_id__in=Subquery(max_id_subquery),
            order_style=2
        ).values('holding_id', 'order_place_date', 'price_stop', 'price_limit')

        # Convert the query result to a DataFrame
        initial_sell_orders_df = pd.DataFrame(list(initial_sell_orders))

        # Convert order_place_date to date format
        initial_sell_orders_df['order_place_date'] = pd.to_datetime(initial_sell_orders_df['order_place_date']).dt.date

        # Rename columns for clarity
        initial_sell_orders_df.rename(columns={
            'order_place_date': 'init_stop_date',
            'price_stop': 'init_stop',
            'price_limit': 'init_limit'
        }, inplace=True)

        return initial_sell_orders_df

    def get_holding_current_stop(self) -> pd.DataFrame:

        # Subquery to get the maximum trade_id for each holding_id
        max_trade_id_subquery = (Order.objects.filter(holding_id=OuterRef('holding_id'))
            .order_by('-trade_id').values('trade_id'))[:1]

        # Query to get holding_sell_order where trade_id is in the previous trade_id list
        sell_orders_with_max_trade_id = (Order.objects.filter(
            trade_id__in=Subquery(max_trade_id_subquery),
            order_style=2
        ))

        # Subquery to get the maximum holding_sell_order_id for each trade_id
        max_sell_order_id_subquery = (
            sell_orders_with_max_trade_id
            .values('trade_id')
            .annotate(max_sell_order_id=Max('order_id'))
            .values('max_sell_order_id'))

        # Query to get all holding_sell_order in the previous holding_sell_order_id list
        last_sell_orders = Order.objects.filter(
            order_id__in=Subquery(max_sell_order_id_subquery)
        ).values('holding_id', 'order_place_date', 'price_stop', 'price_limit', 'trade_id')

        # Convert the query result to a DataFrame
        last_sell_orders_df = pd.DataFrame(list(last_sell_orders))

        # Convert order_place_date to date format
        last_sell_orders_df['order_place_date'] = pd.to_datetime(last_sell_orders_df['order_place_date']).dt.date

        # Rename columns for clarity
        last_sell_orders_df.rename(columns={
            'order_place_date': 'stop_date',
            'price_stop': 'stop',
            'price_limit': 'limit',
        }, inplace=True)

        return last_sell_orders_df

    def get_trading_info(self, holdings_df: DataFrame) -> pd.DataFrame:
        # Step 2. attach Trade info
        trade_phases = Trade.objects.filter(trade_id__in=holdings_df['trade_id'].tolist()
        ).values('trade_id', 'trade_phase')
        # Convert the query result to a DataFrame
        trade_phases_df = pd.DataFrame(list(trade_phases))
        return trade_phases_df

    def get_market_benchmark(self, symbols) -> pd.DataFrame:

        # get current stock & previous day stock as benchmark
        latest_bar = self.TradingResearch.get_stock_hist_bars(True, symbols, 1)
        benchmark = self.TradingResearch.get_stock_hist_bars(True, symbols, 2)

        # Convert the fetched rows into pandas DataFrames
        latest_bar_df = pd.DataFrame(latest_bar)
        latest_bar_df = latest_bar_df[['symbol', 'date', 'close']]
        benchmark_df = pd.DataFrame(benchmark)
        benchmark_df = benchmark_df[['symbol', 'date', 'close']]
        benchmark_df.rename(columns={'date': 'bk_date', 'close': 'bk_close'}, inplace=True)

        # Merge the DataFrames on the 'symbol' column
        merged_df = pd.merge(latest_bar_df, benchmark_df, on='symbol', how='left')
        return merged_df

    def get_current_position(self, holdings: QuerySet[Holding]) -> pd.DataFrame:

        # Fetch and sum the quantity_final from transaction
        transaction = (
            Transaction.objects.filter(holding__in=holdings)
            .annotate(
                trade_is_finished=Subquery(
                    Trade.objects.filter(trade_id=OuterRef('trade_id')).values('is_finished')[:1]
                )
            )
           .filter(Q(trade_is_finished=False) | Q(trade_is_finished__isnull=True))
           .annotate(amount=F('quantity_final') * F('price_final'))
           .values('holding_id')
           .annotate(
                init_tran_id = Min('transaction_id'),
                quantity=Sum('quantity_final'),
                invest=Sum('amount'),
                price=Sum('amount') / Sum('quantity_final')
           ))

        transaction_df = pd.DataFrame(list(transaction), columns=['holding_id', 'init_tran_id', 'quantity', 'invest', 'price'])

        return transaction_df

    def get_init_position(self, transaction_ids:List) -> pd.DataFrame:

        # Retrieve the transaction record
        init_transactions = (
            Transaction.objects.filter(transaction_id__in=transaction_ids)
            .values('holding_id', 'quantity_final', 'price_final')
        )
        # Convert the query result to a DataFrame and rename fields
        init_transactions_df = pd.DataFrame(list(init_transactions))
        init_transactions_df.rename(columns={'quantity_final': 'init_quantity','price_final': 'init_price'}, inplace=True)
        init_transactions_df['init_invest'] = init_transactions_df['init_quantity'] * init_transactions_df['init_price']

        return init_transactions_df

    def attach_today_delta(self, final_df: pd.DataFrame) -> (pd.DataFrame, date):
        max_date = final_df['date'].max()
        max_date = datetime.combine(max_date, datetime.min.time())
        max_date = timezone.make_aware(max_date, timezone.get_current_timezone())
        today_transactions = Transaction.objects.filter(date=max_date)
        if today_transactions.exists():
            today_transactions_df = pd.DataFrame(list(today_transactions.values('holding_id', 'quantity_final', 'price_final')))
            today_transactions_df.rename(columns={'price_final': 'today_price', 'quantity_final': 'today_quantity'}, inplace=True)
            final_df = pd.merge(final_df, today_transactions_df, on='holding_id', how='left').fillna(0)
            final_df['delta'] = final_df['today_quantity'] * (final_df['bk_close'].astype(float) - final_df['today_price'].astype(float))
        else:
            final_df['delta'] = 0
            final_df['delta'] = final_df['delta'].astype(float)

        return final_df, max_date

    def calc_market_value_trand(self, final_df: pd.DataFrame):

        # Step 2.a Calculate market value
        final_df['market'] = final_df['quantity'] * final_df['close']
        final_df['bk_market'] = final_df['quantity'] * final_df['bk_close']
        # Step 2.b Calculate daily change in position & percent
        final_df['chg'] = final_df['close'] - final_df['bk_close']
        final_df['chg_pct'] = ((final_df['chg'] / final_df['bk_close']) * 100).round(2)
        final_df['chg_position'] = final_df['quantity'] * final_df['chg'] + final_df['delta']
        final_df['chg_trend'] = final_df['chg'].apply(lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "-"))

    def calc_risk_vs_gain(self, final_df: pd.DataFrame):
        # Gain
        final_df['gain_pct'] =(final_df['close'].apply(float) - final_df['price'].apply(float)) / final_df['price'].apply(float) * 100
        final_df['gain'] = final_df['price'].apply(float) * final_df['quantity'].apply(float) * final_df['gain_pct'] / 100
        final_df['gain_trend'] = final_df['gain'].apply(lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "-"))
        # Risk
        final_df['risk_pct'] = ((final_df['stop'].apply(float) + final_df['limit'].apply(float)) / 2 - final_df['price'].apply(float)) / final_df['price'].apply(float) * 100
        final_df['risk'] = final_df['price'].apply(float) * final_df['quantity'].apply(float) * final_df['risk_pct'] / 100
        final_df['risk_trend'] = final_df['risk'].apply(lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "-"))
        # Distance
        final_df['dist'] = final_df['gain'] - final_df['risk']
        final_df['dist_pct'] = final_df['dist'].apply(float) / final_df['invest'].apply(float) * 100

    def calc_goal(self, final_df: pd.DataFrame):
        # Calculate the goal
        final_df['init_risk'] = final_df['init_quantity'] * (final_df['init_price'] - (final_df['init_stop'] + final_df['init_limit']) / 2)
        final_df['init_risk_pct'] = final_df['init_risk'] / final_df['init_invest'] * 100

        # # Retrieve the UserStaticSetting record for the given user_id
        # user_static_setting = get_object_or_404(UserStaticSetting, user_id=user_id)
        # expect_gain_risk_ratio = user_static_setting.expect_gain_risk_ratio