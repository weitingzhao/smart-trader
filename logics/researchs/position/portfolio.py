import json
import pandas as pd
from typing import List

from pandas.core.interchange.dataframe_protocol import DataFrame

from logics.service import Service
from .position_base import PositionBase
from django.db.models.query import QuerySet
from decimal import Decimal
from django.http import JsonResponse
from apps.common.models import *
from django.shortcuts import render


class Portfolio(PositionBase):

    def __init__(self, service: Service):
        super().__init__(service)

    def balance_history(self, portfolio: Portfolio) -> pd.DataFrame:

        holdings = Holding.objects.filter(portfolio=portfolio)
        if len(holdings) <= 0:
            return None

        # Step 0. Convert holdings to DataFrame
        holding_df = pd.DataFrame(list(holdings.values()))
        holding_df.rename(columns={'symbol_id': 'symbol'}, inplace=True)
        symbols_df = pd.DataFrame({'symbol': holding_df['symbol'].unique()})


        # Step 1. Attach data
        # Step 1.a fetch transaction data
        transactions_df = pd.merge(self.get_transactions(holding_df), holding_df, on='symbol', how='left')
        # Step 1.b fetch full symbol data
        full_market_df = pd.merge(symbols_df, self.get_market_data(symbols_df,  transactions_df['date'].min()), on='symbol', how='left').fillna(0)
        # Step 1.c fetch funding data
        funding_df = self.get_funding(portfolio)
        # Step 1.d fetch cash balance data
        cash_balance_df = self.get_cash_balance(portfolio)


        # Step 2 Calculate
        # step 2.a pivot transaction & full_market by symbol
        transactions_df = self.pivot_transaction(transactions_df)
        full_market_df = self.pivot_market_data(full_market_df)


        # Step 3. Merge all data
        # Merge the full date range with daily_balance_df
        balance_df = pd.merge(full_market_df, transactions_df, on='date', how='left').fillna(0)
        # Merge the full date range with daily_balance_df
        balance_df = pd.merge(balance_df, funding_df[['date', 'funding']], on='date', how='left').fillna(0)
        # Forward fill the cash_mm values to fill any missing dates
        balance_df = pd.merge(balance_df, cash_balance_df[['date', 'cash_mm', 'money_market', 'cash']], on='date', how='left').fillna(0)


        # Step 4. Calculate balance
        balance_df = self.cumulative_sum_pivoted_columns(symbols_df, balance_df)
        balance_df = self.calculate_balance(balance_df)

        return balance_df

    def balance_calendar(self, portfolio: Portfolio) -> pd.DataFrame:

        balance_df = self.balance_history(portfolio)
        # Step 1.
        # calculate margin
        balance_df['margin'] = balance_df['total_market'] - balance_df['total_asset'] + balance_df['funding']
        balance_df['margin_diff'] = balance_df['margin'].diff()
        balance_df['margin_diff_pct'] = (balance_df['margin_diff'] / balance_df['total_market'].shift(1)) * 100

        # Calculate asset growth percentage
        balance_df['asset_growth_pct'] = (balance_df['margin'] / balance_df['total_asset']) * 100
        # Calculate invest growth percentage
        balance_df['invest_growth_pct'] = (balance_df['margin'] / balance_df['total_invest']) * 100

        # Step 2.
        # compare with index
        # Determine the date range
        start_date = (balance_df['date'].min() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = balance_df['date'].max().strftime('%Y-%m-%d')

        # Define the benchmarks
        benchmarks = ['^IXIC', '^DJI', '^GSPC']
        # Get stock index bars for the benchmarks
        benchmark_data = self.TradingResearch.get_stock_hist_bars_by_date(benchmarks, start_date, end_date)
        # Convert time to date and remove the time part
        benchmark_data['date'] = pd.to_datetime(benchmark_data['time']).dt.date
        # Pivot benchmark_data by date to get the close prices for each symbol
        benchmark_data_pivot = benchmark_data.pivot(index='date', columns='symbol', values='close').reset_index()
        # Calculate the difference and percentage change for each benchmark
        for benchmark in ['^DJI', '^GSPC', '^IXIC']:
            benchmark_data_pivot[f'{benchmark}_diff'] = benchmark_data_pivot[benchmark].diff()
            benchmark_data_pivot[f'{benchmark}_diff_pct'] = (
                benchmark_data_pivot[f'{benchmark}_diff'] / benchmark_data_pivot[benchmark].shift(1)) * 100

        # Merge benchmark data with balance_df
        balance_df = pd.merge(balance_df, benchmark_data_pivot, on='date', how='left')

        if balance_df is None:
            return None



        return balance_df


    def get_transactions(self, holding_df: DataFrame ) -> pd.DataFrame:

        holding_ids = holding_df['holding_id'].tolist()

        # Fetch transaction data
        transactions = Transaction.objects.filter(holding_id__in=holding_ids)
        transactions_df = pd.DataFrame(list(transactions.values()))
        transactions_df['date'] = pd.to_datetime(transactions_df['date']).dt.date
        transactions_df['quantity'] = transactions_df.apply(
            lambda row: row['quantity_final'] if row['transaction_type'] == '1' else -row['quantity_final'],
            axis=1
        )
        transactions_df['holding'] = transactions_df.apply(
            lambda row: row['quantity_final'] * row['price_final']
            if row['transaction_type'] == '1' else -row['quantity_final'] * row['price_final'] - row['commission'],
            axis=1
        )
        transactions_df = transactions_df.drop(columns=['buy_order_id', 'sell_order_id'])

        # Group by holding and trade_id
        transactions_df['symbol'] = transactions_df['holding_id'].map(holding_df.set_index('holding_id')['symbol'])
        transactions_df = transactions_df.groupby(['symbol', 'date']).agg(
            quantity_sum=pd.NamedAgg(column='quantity', aggfunc='sum'),
            holding_sum=pd.NamedAgg(column='holding', aggfunc='sum'),
        ).reset_index()
        transactions_df = transactions_df.rename(columns={'quantity_sum': 'quantity', 'holding_sum': 'holding'})

        return transactions_df

    def get_market_data(self, symbols_df: DataFrame, min_date: pd.Timestamp) -> pd.DataFrame:
        today = pd.to_datetime('today').date()

        # Create a DataFrame with all symbols
        market_data = MarketStockHistoricalBarsByDay.objects.filter(
            symbol__in=symbols_df['symbol'].tolist(),
            time__date__range=[min_date, today]
        ).values('symbol', 'time', 'close')

        # Convert market data to DataFrame
        market_data_df = pd.DataFrame(list(market_data))
        market_data_df['date'] = pd.to_datetime(market_data_df['time']).dt.date

        return market_data_df

    def get_funding(self, portfolio: Portfolio) -> pd.DataFrame:
        # Step 5. Get funding records
        funding_records = Funding.objects.filter(portfolio=portfolio)
        funding_df = pd.DataFrame(list(funding_records.values()))
        funding_df['completion_date'] = pd.to_datetime(funding_df['completion_date']).dt.date
        funding_df = funding_df.rename(columns={'completion_date': 'date', 'amount': 'funding'})
        return funding_df

    def get_cash_balance(self, portfolio: Portfolio) -> pd.DataFrame:
        # Step 6. Get cash balance records
        cash_balances = CashBalance.objects.filter(portfolio=portfolio)
        cash_balance_df = pd.DataFrame(list(cash_balances.values()))
        cash_balance_df['as_of_date'] = pd.to_datetime(cash_balance_df['as_of_date']).dt.date
        cash_balance_df['cash_mm'] = cash_balance_df['money_market'] + cash_balance_df['cash']
        cash_balance_df = cash_balance_df.rename(columns={'as_of_date': 'date'})
        return cash_balance_df

    def pivot_transaction(self, transactions_df: DataFrame) -> pd.DataFrame:
        # pivot transactions by symbol
        transactions_df = transactions_df.pivot(index='date', columns='symbol', values=['quantity', 'holding'])
        transactions_df.columns = [
            f"q/{col[1]}" if col[0] == 'quantity' else f"h/{col[1]}" for col in transactions_df.columns.values
        ]
        # Reset index to make 'date' a column again
        transactions_df = transactions_df.reset_index()
        pd.set_option('future.no_silent_downcasting', True)
        transactions_df = transactions_df.fillna(0).infer_objects(copy=False)
        return transactions_df

    def pivot_market_data(self, full_market_data_df: DataFrame) -> pd.DataFrame:
        # Pivot the resulting DataFrame by symbol
         return full_market_data_df.pivot(index='date', columns='symbol', values='close').reset_index()

    def cumulative_sum_pivoted_columns(self, symbols_df: DataFrame, balance_df: DataFrame) -> pd.DataFrame:
        # Step 4.1 Apply cumulative sum to the pivoted columns
        for col in balance_df.columns:
            if col.startswith('q/') or col.startswith('h/'):
                balance_df[col] = balance_df[col].cumsum()

        # Step 4.2 Calculate market value for each symbol
        for symbol in symbols_df['symbol']:
            quantity_col = f'q/{symbol}'
            if quantity_col in balance_df.columns:
                balance_df[f'mv/{symbol}'] = balance_df[quantity_col] * balance_df[symbol]

        # Step 4.3 Calculate balance_holding by summing all h/{symbol} columns
        balance_df['balance_holding'] = balance_df[[col for col in balance_df.columns if col.startswith('h/')]].sum(
            axis=1)
        # Step 4.4 Calculate balance_mv by summing all mv/{symbol} columns
        balance_df['balance_mv'] = balance_df[[col for col in balance_df.columns if col.startswith('mv/')]].sum(axis=1)
        return balance_df

    def calculate_balance(self, balance_df: pd.DataFrame) -> pd.DataFrame:
        # Step 7. Calculate column under balance_df
        # Calculate the cash & money market
        balance_df['cash_mm_daily'] = balance_df['cash_mm'].replace(0, pd.NA).ffill().fillna(0)
        balance_df = balance_df.drop(columns=['cash_mm'])
        # balance_df['funding']
        # Calculate total capital and market value
        balance_df['total_market'] = balance_df['balance_mv'].apply(Decimal) + balance_df['cash_mm_daily']
        balance_df['total_asset'] = balance_df['balance_holding'] + balance_df['cash_mm_daily'] + balance_df['funding']
        balance_df['total_invest'] = balance_df['balance_holding']
        return balance_df