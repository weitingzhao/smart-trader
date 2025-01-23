from ..treading.trading_research import TradingResearch
from ...service import Service
from ..base_research import BaseResearch
import pandas as pd
import numpy as np
from apps.common.models import *
from datetime import datetime, timedelta, date
from pandas.core.interchange.dataframe_protocol import DataFrame

class PositionBase(BaseResearch):

    def __init__(self, service: Service):
        super().__init__(service)
        self.TradingResearch = TradingResearch(self.service, None)

    def get_cash_balance_by_date(self, snapshot_date: date ) -> pd.DataFrame:
        earliest_date = CashBalance.objects.filter(
            as_of_date__lt=snapshot_date - timedelta(days=1)).order_by('-as_of_date').first().as_of_date
        now = date(snapshot_date.year, snapshot_date.month, snapshot_date.day)
        # Ensure earliest_date and max_date are timezone-naive
        # Step 2: Get all CashBalance records with as_of_date >= earliest_date
        cash_balances = CashBalance.objects.filter(as_of_date__gte=earliest_date).values('as_of_date', 'money_market', 'cash')
        cash_balance_df = pd.DataFrame(list(cash_balances))
        cash_balance_df['as_of_date'] = pd.to_datetime(cash_balance_df['as_of_date']).dt.date
        cash_balance_df = cash_balance_df.rename(columns={'as_of_date': 'cash_date'})
        cash_balance_df['cash_mm'] = cash_balance_df['money_market'] + cash_balance_df['cash']
        # Create a date range from earliest_date to max_date
        date_range = pd.date_range(start=earliest_date, end=now)
        # Reindex cash_balance_df to the date range
        cash_balance_df = cash_balance_df.set_index('cash_date').reindex(date_range).rename_axis('cash_date').reset_index()
        cash_balance_df['cash_mm'] = cash_balance_df['cash_mm'].replace(0, np.nan).ffill().fillna(0)

        return cash_balance_df

    def get_trading_info(self, holdings_df: DataFrame) -> pd.DataFrame:
        # Step 2. attach Trade info
        trade_phases = Trade.objects.filter(trade_id__in=holdings_df['trade_id'].tolist()
        ).values('trade_id', 'trade_phase', 'trade_phase_rating','trade_source', 'strategy_id', 'strategy__short_name')
        # Convert the query result to a DataFrame
        trade_phases_df = pd.DataFrame(list(trade_phases))
        trade_phases_df['strategy_id'] = trade_phases_df['strategy_id'].fillna(0).astype(int)
        return trade_phases_df