import re
import os
from datetime import datetime as dt
from apps.common.models import *
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget


class SnapshotResource(resources.ModelResource):


    def before_import(self, dataset, **kwargs):

        try:
            filename = kwargs['file_name']
            match = re.search(r'_(\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2}\.\d{3}Z)\.csv$', filename)
            if match:
                date_str = match.group(1)
                self.date_obj = dt.strptime(date_str, '%Y-%m-%dT%H_%M_%S.%fZ').date()
        except KeyError:
            try:
                filename = self.import_job.file.name
                match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
                # print("filename: ", filename)
                # print("match: ", match)
                if match:
                    date_str = match.group(0)
                    # print("date_str: ", date_str)
                    self.date_obj = dt.strptime(date_str, '%Y-%m-%d').date()
                    # print("date_obj: ", self.date_obj)
            except AttributeError:
                self.date_obj = None

    def before_import_row(self, row, **kwargs):
        for key, value in row.items():
            if value == "N/A":
                row[key] = None
        if self.date_obj:
            row['time'] = self.date_obj
            # print(f"row - Date===========>: {row['time']}")

    def skip_row(self, instance, original, row, import_validation_errors=None):
        return self._meta.model.objects.filter(
            symbol=instance.symbol,
            time=instance.time
        ).exists()

    # def before_save_instance(self, instance, using_transactions, dry_run, **kwargs):
    #     if not instance.symbol:
    #         raise ValueError(f"Symbol '{instance.symbol}' not found in MarketSymbol table.")

    # def skip_row(self, instance, original, dry_run, **kwargs):
    #     return not MarketSymbol.objects.filter(symbol=instance.symbol).exists()

    symbol = fields.Field( column_name='Symbol', attribute='symbol',
        widget=ForeignKeyWidget(MarketSymbol, 'symbol') )

    class Meta:
        abstract = True
        fields = ('id', 'symbol', 'time')

# Screening
class SnapshotScreeningResource(SnapshotResource):

    def before_import(self, dataset, **kwargs):

        super().before_import(dataset, **kwargs)
        self.ref_screening_id = None  # Initialize screening_id as None

        try:
            filename = kwargs['file_name']
        except KeyError:
            try:
                filename = os.path.basename(self.import_job.file.name)
            except AttributeError:
                filename = None
        # print(f"before filename: {filename}")

        if filename is not None:
            screenings = Screening.objects.all()
            for screening in screenings:
                if filename.startswith(screening.file_pattern):
                    self.ref_screening_id = screening.screening_id
                    break
        # print(f"screening_id: {self.screening_id}")

    def before_import_row(self, row, **kwargs):
        super().before_import_row(row, **kwargs)
        if self.ref_screening_id is None:
            raise ValueError("screening_id is not set. Cannot import row without screening_id.")
        row['screening'] = self.ref_screening_id
        # print(f"row:: {row}")

    def skip_row(self, instance, original, row, import_validation_errors=None):
        return self._meta.model.objects.filter(
            symbol=instance.symbol,
            time=instance.time,
            screening=instance.screening
        ).exists()


    class Meta:
        name = 'SnapshotScreening'
        model = SnapshotScreening
        fields = SnapshotResource.Meta.fields + ('screening',)


# Overview
class SnapshotOverviewResource(SnapshotResource):

    name = fields.Field(column_name='Name', attribute='name')
    # Rating
    setup_rating = fields.Field(column_name='ChartMill Setup Rating', attribute='setup_rating')
    technical_rating = fields.Field(column_name='ChartMill Technical Rating', attribute='technical_rating')
    fundamental_rating = fields.Field(column_name='ChartMill Fundamental Rating', attribute='fundamental_rating')
    relative_strength = fields.Field(column_name='ChartMill Relative Strength', attribute='relative_strength')
    # Performance
    one_month_performance = fields.Field(column_name='1 Month Performance', attribute='one_month_performance')
    three_month_performance = fields.Field(column_name='3 Month Performance', attribute='three_month_performance')
    six_month_performance = fields.Field(column_name='6 Month Performance', attribute='six_month_performance')
    # P/E Liquidity
    percent_change = fields.Field(column_name='% Change', attribute='percent_change')
    price_earnings = fields.Field(column_name='Price/Earnings', attribute='price_earnings')
    market_cap = fields.Field(column_name='Market Cap', attribute='market_cap')
    avg_volume_50 = fields.Field(column_name='Avg Volume(50)', attribute='avg_volume_50')

    class Meta:
        name = 'SnapshotOverview'
        model = SnapshotOverview
        fields =  SnapshotResource.Meta.fields + (
            'name',
            # Rating
            'setup_rating', 'technical_rating',  'fundamental_rating', 'relative_strength',
            # Performance
            'one_month_performance', 'three_month_performance', 'six_month_performance',
            # P/E Liquidity
             'percent_change', 'price_earnings', 'market_cap', 'avg_volume_50',
        )

# Technical
class SnapshotTechnicalResource(SnapshotResource):

    # Volatility
    lower_bollinger_band = fields.Field(column_name='Lower Bollinger Band', attribute='lower_bollinger_band')
    upper_bollinger_band = fields.Field(column_name='Upper Bollinger Band', attribute='upper_bollinger_band')
    # Momentum Direction
    RSI_14 = fields.Field(column_name='RSI(14)', attribute='RSI_14')
    MACD_12_26_9 = fields.Field(column_name='MACD(12,26,9)', attribute='MACD_12_26_9')
    # Trend
    ADX_14 = fields.Field(column_name='ADX(14)', attribute='ADX_14')
    # Overhead Supply Pressure
    asset_turnover = fields.Field(column_name='Asset Turnover', attribute='asset_turnover')
    # Price Optimal Range
    # Gauge Volume Strength
    daily_effective_ratio = fields.Field(column_name='Daily Effective Ratio', attribute='daily_effective_ratio')

    class Meta:
        name = 'SnapshotTechnical'
        model = SnapshotTechnical
        fields = SnapshotResource.Meta.fields + (
            # Volatility
            'lower_bollinger_band', 'upper_bollinger_band',
            # Momentum Direction
            'RSI_14', 'MACD_12_26_9',
            # Trend
            'ADX_14',
            # Overhead Supply Pressure
            'asset_turnover',
            # Gauge Volume Strength
            'daily_effective_ratio',
        )

# Fundamental
class SnapshotFundamentalResource(SnapshotResource):

    # Valuation
    valuation_rating = fields.Field(column_name='ChartMill Valuation Rating', attribute='valuation_rating')
    price_FCF = fields.Field(column_name='Price/FCF', attribute='price_FCF')
    PEG_next_year = fields.Field(column_name='PEG (Next Year)', attribute='PEG_next_year')
    # Growth
    growth_rating = fields.Field(column_name='ChartMill Growth Rating', attribute='growth_rating')
    EPS_growth_Q2Q = fields.Field(column_name='EPS growth Q2Q', attribute='EPS_growth_Q2Q')
    # Profitability
    profitability_rating = fields.Field(column_name='ChartMill Profitability Rating', attribute='profitability_rating')
    high_growth_momentum_rating = fields.Field(column_name='ChartMill High Growth Momentum Rating', attribute='high_growth_momentum_rating')
    avg_ROIC_5y = fields.Field(column_name='Avg ROIC(5Y)', attribute='avg_ROIC_5y')
    FCF_margin = fields.Field(column_name='FCF Margin', attribute='FCF_margin')
    # Financial Health
    health_rating = fields.Field(column_name='ChartMill Health Rating', attribute='health_rating')
    interest_coverage = fields.Field(column_name='Interest Coverage', attribute='interest_coverage')
    # # Stock Share
    shares_outstanding_5y_change = fields.Field(column_name='Shares Outstanding 5Y Change', attribute='shares_outstanding_5y_change')

    class Meta:
        name = 'SnapshotFundamental'
        model = SnapshotFundamental
        fields = SnapshotResource.Meta.fields + (
            # Valuation
            'valuation_rating', 'price_FCF', 'PEG_next_year',
            # Growth
            'growth_rating', 'EPS_growth_Q2Q',
            # Profitability
            'profitability_rating', 'high_growth_momentum_rating', 'avg_ROIC_5y', 'FCF_margin',
            # Financial Health
            'health_rating', 'interest_coverage',
            # # Stock Share
            'shares_outstanding_5y_change',
        )

# Setup
class SnapshotSetupResource(SnapshotResource):

    market_cap = fields.Field(column_name='Market Cap', attribute='market_cap')
    GICS_sector = fields.Field(column_name='GICS Sector', attribute='GICS_sector')
    high_52_week = fields.Field(column_name='52 Week High', attribute='high_52_week')
    weekly_support = fields.Field(column_name='Weekly Support WS1.', attribute='weekly_support')

    class Meta:
        name = 'SnapshotSetup'
        model = SnapshotSetup
        fields = SnapshotResource.Meta.fields + (
            'market_cap', 'GICS_sector', 'high_52_week', 'weekly_support',
        )

# Bull Flag
class SnapshotBullFlagResource(SnapshotResource):

    #Bull
    bull_indicator = fields.Field(column_name='Chartmill Bull Indicator', attribute='bull_indicator')
    bull_flag = fields.Field(column_name='Bull Flag', attribute='bull_flag')
    weekly_bull_flag = fields.Field(column_name='Weekly Bull Flag', attribute='weekly_bull_flag')
    bullish_engulfing_daily = fields.Field(column_name='Bullish Engulfing Daily', attribute='bullish_engulfing_daily')
    bullish_hammer_daily = fields.Field(column_name='Bullish Hammer Daily', attribute='bullish_hammer_daily')
    bullish_harami_daily = fields.Field(column_name='Bullish Harami Daily', attribute='bullish_harami_daily')
    bullish_engulfing_weekly = fields.Field(column_name='Bullish Engulfing Weekly', attribute='bullish_engulfing_weekly')
    bullish_hammer_weekly = fields.Field(column_name='Bullish Hammer Weekly', attribute='bullish_hammer_weekly')
    bullish_harami_weekly = fields.Field(column_name='Bullish Harami Weekly', attribute='bullish_harami_weekly')
    #Flag
    flag_type = fields.Field(column_name='Flag Type', attribute='flag_type')
    flag_pole = fields.Field(column_name='Flag Pole', attribute='flag_pole')
    flag_length = fields.Field(column_name='Flag Length', attribute='flag_length')
    flag_width = fields.Field(column_name='Flag Width', attribute='flag_width')
    weekly_flag_type = fields.Field(column_name='Weekly Flag Type', attribute='weekly_flag_type')

    class Meta:
        name = 'SnapshotBullFlag'
        model = SnapshotBullFlag
        fields = SnapshotResource.Meta.fields + (
            # Bull
            'bull_indicator', 'bull_flag', 'weekly_bull_flag', 'bullish_engulfing_daily', 'bullish_hammer_daily',
            'bullish_harami_daily', 'bullish_engulfing_weekly', 'bullish_hammer_weekly', 'bullish_harami_weekly',
            # Flag
            'flag_type', 'flag_pole', 'flag_length', 'flag_width', 'weekly_flag_type',
        )