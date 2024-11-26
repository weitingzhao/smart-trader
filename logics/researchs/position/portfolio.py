import json
import pandas as pd
from typing import List
import datetime

from pandas import DataFrame
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

    def balance_history(self, portfolio: Portfolio, cutoff_date: datetime.date = None) -> pd.DataFrame| None:

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
        # Step 1.e fetch holding_sell_order data
        sell_order_df = self.get_holding_sell_order(holding_df)

        # Step 2 Calculate
        # step 2.a pivot transaction & full_market by symbol
        transactions_df = self.pivot_transaction(transactions_df)
        full_market_df = self.pivot_market_data(full_market_df)
        # Step 2.b pivot sell_order by holding_id and date
        sell_order_df = self.pivot_sell_order(sell_order_df)

        # Step 3. Merge all data
        # Merge the full date range with daily_balance_df
        balance_df = pd.merge(full_market_df, transactions_df, on='date', how='left').fillna(0)
        # Merge the full date range with daily_balance_df
        balance_df = pd.merge(balance_df, funding_df[['date', 'funding']], on='date', how='left').fillna(0)
        # Forward fill the cash_mm values to fill any missing dates
        balance_df = pd.merge(balance_df, cash_balance_df[['date', 'cash_mm', 'money_market', 'cash']], on='date', how='left').fillna(0)
        # Merge sell_order data
        balance_df = pd.merge(balance_df, sell_order_df, on='date', how='left')

        # Step 4. Calculate balance
        balance_df = self.cumulative_sum_pivoted_columns(symbols_df, balance_df)
        balance_df = self.calculate_balance(balance_df)
        balance_df = self.calculate_stop_limit(balance_df)

        # Filter data to include only dates greater than 2024-10-31
        if cutoff_date:
            balance_df = balance_df[balance_df['date'] > cutoff_date]

        return balance_df

    def balance_calendar(self, portfolio: Portfolio) -> pd.DataFrame| None:

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

    def benchmark(self, portfolio: Portfolio, cutoff_date: datetime.date) -> DataFrame | None:
        calendar_df = self.balance_calendar(portfolio)

        # Filter data to include only dates greater than 2024-10-31
        calendar_df = calendar_df[calendar_df['date'] > cutoff_date]

        # List of columns to process
        columns = ['margin', '^IXIC', '^DJI', '^GSPC']
        for col in columns:
            # Convert diff_pct to growth factor
            calendar_df[f'{col}_growth_factor'] = calendar_df[f'{col}_diff_pct'] / 100 + 1
            calendar_df[f'{col}_growth_factor'] = calendar_df[f'{col}_growth_factor'].astype(float)
            calendar_df[f'{col}_perf'] = calendar_df[f'{col}_growth_factor'].cumprod()
            calendar_df.loc[0, f'{col}_perf'] = 1
            calendar_df[f'{col}_perf'] = calendar_df[f'{col}_perf'].round(4)
            # Forward fill NaN values
            calendar_df[f'{col}_perf'] = calendar_df[f'{col}_perf'].ffill()

        if calendar_df is None:
            return None
        # Remove rows where the 'date' column is NaN
        calendar_df = calendar_df.dropna(subset=['date'])
        return calendar_df



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

    def get_holding_sell_order(self, holding_df: DataFrame) -> pd.DataFrame:
        holding_ids = holding_df['holding_id'].tolist()
        sell_orders = HoldingSellOrder.objects.filter(holding_id__in=holding_ids).values(
            'holding_sell_order_id', 'holding_id', 'is_obsolete', 'order_place_date', 'quantity_target', 'price_stop', 'price_limit'
        )
        sell_order_df = pd.DataFrame(list(sell_orders))
        sell_order_df['order_place_date'] = pd.to_datetime(sell_order_df['order_place_date']).dt.date
        sell_order_df = pd.merge(sell_order_df, holding_df[['holding_id', 'symbol']], on='holding_id', how='left')

        # Fetch transactions by sell_order_id
        transactions = Transaction.objects.filter(sell_order_id__in=sell_order_df['holding_sell_order_id'].tolist())
        transactions_df = pd.DataFrame(list(transactions.values()))
        transactions_df['date'] = pd.to_datetime(transactions_df['date']).dt.date

        # Calculate is_filled
        sell_order_df['is_filled'] = sell_order_df.apply(
            lambda row: True if transactions_df[transactions_df['sell_order_id'] == row['holding_sell_order_id']]['quantity_final'].sum()
                             == row['quantity_target'] else False,axis=1)

        # Add status column
        sell_order_df['status'] = sell_order_df.apply(
            lambda row: 'Obsolete' if row['is_obsolete'] else 'Open', axis=1
        )

        # Add fill_date column
        sell_order_df['fill_date'] = sell_order_df.apply(
            lambda row: transactions_df[transactions_df['sell_order_id'] == row['holding_sell_order_id']]['date'].max()
            if row['is_filled'] else pd.NaT, axis=1
        )

        # Calculate baseline
        sell_order_df['baseline'] = sell_order_df['quantity_target'] * ((sell_order_df['price_stop'] + sell_order_df['price_limit']) / 2)
        # Rename columns
        sell_order_df.rename(columns={'order_place_date':'date'}, inplace=True)
        # Drop price_stop and price_limit columns
        sell_order_df.drop(columns=['is_filled', 'quantity_target', 'price_stop', 'price_limit'], inplace=True)

        # Compare fill_date with date and update status and fill_date
        sell_order_df.loc[sell_order_df['fill_date'] == sell_order_df['date'], 'status'] = 'Filled'
        sell_order_df.loc[sell_order_df['fill_date'] == sell_order_df['date'], 'fill_date'] = pd.NaT


        # Extract records with non-NaN fill_date
        filled_records = sell_order_df[sell_order_df['fill_date'].notna()].copy()
        filled_records['date'] = filled_records['fill_date']
        filled_records['status'] = 'Filled'
        filled_records['holding_sell_order_id'] = -filled_records['holding_sell_order_id']
        filled_records = filled_records[['holding_sell_order_id', 'holding_id', 'is_obsolete', 'date', 'symbol', 'status', 'fill_date','baseline']]
        # Append filled records back to sell_order_df
        sell_order_df = pd.concat([sell_order_df, filled_records])

        return sell_order_df


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

    def pivot_sell_order(self, sell_order_df: DataFrame) -> pd.DataFrame:
        # Pivot the sell_order_df by date and symbol for baseline and status
        sell_order_df = sell_order_df.pivot(index='date', columns='symbol', values=['baseline', 'status'])
        # Rename columns to add prefixes
        sell_order_df.columns = [
            f"b/{col[1]}" if col[0] == 'baseline' else f"s/{col[1]}" for col in sell_order_df.columns.values
        ]
        # Reset index to make 'date' a column again
        sell_order_df = sell_order_df.reset_index()
        return sell_order_df


    def cumulative_sum_pivoted_columns(self, symbols_df: DataFrame, balance_df: DataFrame) -> pd.DataFrame:
        # Step 4.1 Apply cumulative sum to the pivoted columns
        for col in balance_df.columns:
            if col.startswith('q/') or col.startswith('h/'):
                balance_df[col] = balance_df[col].cumsum()

        # Loop through q/ columns again and set h/ values to 0 if q/ value is 0
        for col in [col for col in balance_df.columns if col.startswith('h/')]:
            balance_df[col] = balance_df.apply(
                lambda row: 0 if row[f'q/{col[2:]}'] == 0 else row[col], axis=1
            )

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

    def calculate_stop_limit(self, balance_df: pd.DataFrame) -> pd.DataFrame:
        # Fill NaN values for s/ columns based on the specified logic

        # /b is baseline /s is status
        for col in balance_df.columns: # column
            if not col.startswith('s/'):
                continue
            last_valid = None
            last_baseline = 0
            for i in range(len(balance_df)): # row
                # /s status
                current_status = balance_df.iloc[i][col]
                if pd.notna(current_status):  # Found a non-NaN value
                    if current_status in ['Obsolete', 'Open']:
                        last_valid = current_status
                    elif current_status == 'Filled':
                        last_valid = None  # Stop forward filling after Filled
                else:
                    if last_valid:  # Fill only if a valid last value exists
                        balance_df.iloc[i, balance_df.columns.get_loc(col)] = last_valid
                # /b baseline
                b_col = f"b/{col[2:]}"
                current_baseline = balance_df.iloc[i][b_col]
                if pd.notna(current_baseline):  # Found a non-NaN value
                    if current_status in ['Obsolete', 'Open']:
                        last_baseline = current_baseline
                        balance_df.iloc[i, balance_df.columns.get_loc(b_col)] = last_baseline
                    elif current_status == 'Filled':
                        last_baseline = 0
                        balance_df.iloc[i, balance_df.columns.get_loc(b_col)] = 0
                    else:
                        last_baseline = 0  # Stop forward filling after Filled
                else:
                    balance_df.iloc[i, balance_df.columns.get_loc(b_col)] = last_baseline

        # Sum all b/ columns
        balance_df['total_baseline'] = balance_df[[col for col in balance_df.columns if col.startswith('b/')]].sum(axis=1)

        return balance_df