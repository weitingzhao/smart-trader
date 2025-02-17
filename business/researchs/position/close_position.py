import pandas as pd
from typing import List
from ...service import Service
from apps.common.models import *
from .position_base import PositionBase
from django.db.models.query import QuerySet
from pandas.core.interchange.dataframe_protocol import DataFrame
from django.db.models import (F,Case, When, Sum, Min, Max, Q, Subquery, OuterRef)


class ClosePosition(PositionBase):

    def __init__(self, service: Service):
        super().__init__(service)

    def Position(self, portfolio: Portfolio, strategy_id: int ) -> pd.DataFrame or None:

        holdings = Holding.objects.filter(portfolio=portfolio)
        if len(holdings) <= 0:
            return None

        # Step 0. Convert holdings to DataFrame
        final_df = pd.DataFrame(list(holdings.values()))
        final_df.rename(columns={'symbol_id': 'symbol'}, inplace=True)

        # Step 1. Attach data
        # Step 1.a Merge the symbol names
        final_df = pd.merge(final_df, self.get_holding_symbol(final_df), on='symbol', how='left')
        # Step 1.b Attach Trades
        trade_df = self.get_trades(holdings)
        # Step 1.c Attach Trade info
        trade_df = pd.merge(trade_df, self.get_trading_info(trade_df), on='trade_id', how='left')

        # Filter trade_df based on strategy_id if strategy_id >= 0
        if strategy_id >= 0:
            trade_df = trade_df[trade_df['strategy_id'] == strategy_id]
            if len(trade_df) <= 0:
                return None

        # Step 1.d Merge to final df
        final_df = pd.merge(final_df, trade_df, on='holding_id', how='inner').fillna(0)
        # Step 1.c Attach stock prices
        final_df = pd.merge(final_df, self.get_stock_prices(final_df), left_on=['symbol', 'exit_date'], right_on=['symbol', 'date'], how='left')
        # Step 1.d Attach initial sell orders
        final_df = pd.merge(final_df, self.get_initial_sell_orders(trade_df['trade_id'].tolist()), on='trade_id', how='left')

        # Step 2. Calculate
        # Step 2.a Calculate performance
        self.calc_performance(final_df)
        # Step 2.b Calculate risk/gain
        self.calc_risk_gain(final_df)

        # Order by exit_date in descending order
        final_df = final_df.sort_values(by='exit_date', ascending=False)

        return final_df

    def summary(self, final_df: pd.DataFrame) -> dict:
        ##### Calculate the summary tab ##############
        data = {
            'total_amt': 0,
            'realized': {
                'net': 0,
                'gain': 0,
                'lost': 0,
            },

            # Profit
            'win_trade': 0,
            'win_inv': 0,
            'win_avg_pct': 0,
            'win_avg': 0,
            'win_avg_days': 0,

            # Loss
            'loss_trade': 0,
            'loss_inv': 0,
            'loss_avg_pct': 0,
            'loss_avg': 0,
            'loss_avg_days': 0,

            # Total & Max
            'max_loss': 0,
            'max_loss_pct': 0,

           # Statistics
            'kelly_criterion': 0,
            'rate': 0,
            'expected': 0,
            'win_loss_ratio': 0,

            # Main Indicator
            'marginal_position_risk': 0,
            'marginal_return_rate': 0,
            'profitability_ratio': 0,
            'profit_efficiency': 0,
        }
        data['total_amt'] = final_df['trade_margin'].count()
        # Part 1. realized G/L gain / loss
        # Calculate realized gain and loss
        data['realized']['gain'] = final_df[final_df['trade_margin'] > 0]['trade_margin'].sum()
        data['realized']['lost'] = final_df[final_df['trade_margin'] < 0]['trade_margin'].sum()
        # Calculate net realized value
        data['realized']['net'] = data['realized']['gain'] + data['realized']['lost']

        # Part 2. calculation
        # Profit
        data['win_trade'] = final_df[final_df['trade_margin'] > 0].shape[0]
        win_trades = final_df[final_df['trade_margin'] > 0]
        if not win_trades.empty:
            data['win_avg_pct'] = (win_trades['trade_margin'].sum() / win_trades['buy_total_value'].sum()) * 100
            data['win_avg'] = win_trades['trade_margin'].sum() / data['win_trade']
            data['win_inv'] = (win_trades['buy_total_value'].sum() / data['win_trade'])
            data['win_avg_days'] = win_trades['held_day'].mean()
        # Loss
        data['loss_trade'] = final_df[final_df['trade_margin'] < 0].shape[0]
        loss_trades = final_df[final_df['trade_margin'] < 0]
        if not loss_trades.empty:
            data['loss_avg_pct'] = (loss_trades['trade_margin'].sum() / loss_trades['buy_total_value'].sum()) * 100
            data['loss_avg'] = loss_trades['trade_margin'].sum() / data['loss_trade']
            data['loss_inv'] = (loss_trades['buy_total_value'].sum() / data['loss_trade'])
            data['loss_avg_days'] = loss_trades['held_day'].mean()

        # Total & Max
        data['max_loss'] = final_df['trade_margin'].min()
        data['max_loss_pct'] = final_df['trade_performance'].min()

        # Statistics
        data['rate'] = data['win_trade'] / (data['win_trade'] + data['loss_trade']) * 100
        data['expected'] = (float(data['rate']) / 100 * float(data['win_avg'])
                - (100 - float(data['rate'])) / 100 * float(data['loss_avg']))
        data['win_loss_ratio'] = data['win_avg'] / abs(data['loss_avg'])
        if data['win_loss_ratio']  == 0:
            data['kelly_criterion'] = 0
        else:
            data['kelly_criterion'] = (float(data['win_loss_ratio']) * float(data['rate'])/100 - (1 - float(data['rate'])/100)) / float(data['win_loss_ratio']) * 100

        # Main Indicator
        data['marginal_position_risk'] =  (data['loss_avg_pct'] /100)* final_df['buy_total_value'].max()
        data['marginal_return_rate'] = float(data['realized']['net']) / abs(float(data['max_loss']))
        data['profitability_ratio'] = float(data['realized']['gain']) / abs(float(data['marginal_position_risk']))
        data['profit_efficiency'] = float(data['realized']['gain'])/float(final_df['buy_total_value'].sum())*100

        return data

    def get_holding_symbol(self, final_df: DataFrame) -> pd.DataFrame:

        # get symbol record by symbol
        symbol_names = MarketSymbol.objects.filter(symbol__in=final_df['symbol']).values('symbol', 'name')
        symbol_names_df = pd.DataFrame(list(symbol_names))
        return symbol_names_df

    def get_trades(self, holdings: QuerySet[Holding]) -> pd.DataFrame:
        # Step 3. trades
        trades = (Transaction.objects.filter(holding__in=holdings)
        .annotate(
            trade_is_finished=Subquery(
                Trade.objects.filter(trade_id=OuterRef('trade_id')).values('is_finished')[:1]
            ),
        )
        .filter(Q(trade_is_finished=True))
        .annotate(amount=F('quantity_final') * F('price_final'))
        .values('trade_id', 'holding_id')
        .annotate(
            init_quantity=Sum(Case(When(transaction_type=1, then=F('quantity_final')))),
            quantity=Sum(Case(When(transaction_type=2, then=F('quantity_final')))),
            buy_total_value=Sum(Case(When(transaction_type=1, then=F('quantity_final') * F('price_final')))),
            buy_average_price=Sum(Case(When(transaction_type=1, then=F('quantity_final') * F('price_final')))) / Sum(
                Case(When(transaction_type=1, then=F('quantity_final')))),
            sell_total_value=Sum(Case(When(transaction_type=2, then=F('quantity_final') * F('price_final')))),
            sell_average_price=Sum(Case(When(transaction_type=2, then=F('quantity_final') * F('price_final')))) / Sum(
                Case(When(transaction_type=2, then=F('quantity_final')))),
            sell_commission=Sum(Case(When(transaction_type=2, then=F('commission')))),
            entry_date=Min('date'),
            exit_date=Max('date'),
        ))
        trade_df = pd.DataFrame(list(trades), columns=[
            'trade_id', 'holding_id', 'init_quantity', 'quantity',
            'buy_total_value', 'buy_average_price',
            'sell_total_value', 'sell_average_price', 'sell_commission',
            'entry_date', 'exit_date'])

        return trade_df

    def get_stock_prices(self, final_df: DataFrame) -> pd.DataFrame:
        # Step 4. Get stock pre-exit-date prices
        symbol_date_pairs = [(row['symbol'], row['exit_date']) for index, row in final_df.iterrows()]
        # Call the get_stock_prices function
        stock_prices_df =  self.TradingResearch.get_stock_prices(symbol_date_pairs, -1)
        return stock_prices_df

    def get_initial_sell_orders(self, trade_ids: List) -> pd.DataFrame:
        initial_sell_orders = Order.objects.filter(
            trade_id__in=trade_ids,
            order_style=2,
        ).values('trade_id').annotate(
            init_sell_order_id=Min('order_id'),
            last_sell_order_id=Max('order_id')
        )
        # Convert to DataFrame
        initial_sell_orders_df = pd.DataFrame(list(initial_sell_orders))

        # get init_stop, init_limit, last_stop, and last_limit
        init_sell_order_ids = initial_sell_orders_df['init_sell_order_id'].tolist()
        last_sell_order_ids = initial_sell_orders_df['last_sell_order_id'].tolist()
        init_sell_orders = Order.objects.filter(
            order_id__in=init_sell_order_ids
        ).values('order_id', 'price_stop', 'price_limit')
        last_sell_orders = Order.objects.filter(
            order_id__in=last_sell_order_ids
        ).values('order_id', 'price_stop', 'price_limit')

        # Convert to DataFrame
        init_sell_orders_df = pd.DataFrame(list(init_sell_orders))
        last_sell_orders_df = pd.DataFrame(list(last_sell_orders))

        # Merge the initial and last sell orders data into initial_sell_orders_df
        initial_sell_orders_df = pd.merge(
            initial_sell_orders_df,
            init_sell_orders_df,
            left_on='init_sell_order_id',
            right_on='order_id',
            how='left',
            suffixes=('', '_init')
        ).drop(columns=['order_id'])
        initial_sell_orders_df = pd.merge(
            initial_sell_orders_df,
            last_sell_orders_df,
            left_on='last_sell_order_id',
            right_on='order_id',
            how='left',
            suffixes=('', '_last')
        ).drop(columns=['order_id'])

        # Rename columns for clarity
        initial_sell_orders_df.rename(columns={
            'price_stop': 'init_stop',
            'price_limit': 'init_limit',
            'price_stop_last': 'last_stop',
            'price_limit_last': 'last_limit'
        }, inplace=True)

        return initial_sell_orders_df

    def calc_performance(self, final_df: DataFrame) -> None:

        # Calculate the "delta day cost" column
        final_df['delta_day_cost'] = (final_df['sell_average_price'].astype(float) - final_df['close'].astype(float)) * \
                                     final_df['quantity'].astype(float)
        final_df['delta_day_cost_rat'] = final_df['delta_day_cost'].astype(float) / final_df['buy_total_value'].astype(
            float) * 100
        final_df['trade_margin'] = final_df['sell_total_value'] - final_df['buy_total_value']
        final_df['trade_performance'] = (final_df['trade_margin'].astype(float) / final_df['buy_total_value'].astype(
            float)) * 100
        final_df['held_day'] = (pd.to_datetime(final_df['exit_date']) - pd.to_datetime(final_df['entry_date'])).dt.days
        # 6.2. Calculate portfolio performance
        model_capital = UserStaticSetting.objects.values_list('capital', flat=True).first()
        final_df['portfolio_trade_performance'] = final_df['trade_margin'].astype(float) / float(model_capital) * 100

    def calc_risk_gain(self, final_df: DataFrame) -> None:

        # Risk / Gain
        final_df['last_risk'] = (
                (final_df['close'].astype(float)
                 - (final_df['last_stop'].astype(float) + final_df['last_limit'].astype(float)) / 2)
                * final_df['quantity'].astype(float)
        )
        final_df['last_risk_ratio'] = (final_df['last_risk'].astype(float) / final_df['buy_total_value'].astype(
            float)) * 100

        final_df['init_risk'] = (
                (final_df['buy_average_price'].astype(float)
                 - (final_df['init_stop'].astype(float) + final_df['init_limit'].astype(float)) / 2)
                * final_df['init_quantity'].astype(float)
        )
        final_df['init_risk_ratio'] = (final_df['init_risk'].astype(float) / final_df['buy_total_value'].astype(
            float)) * 100


