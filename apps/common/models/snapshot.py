from django.db import models
from apps.common.models import *
from timescale.db.models.models import TimescaleModel


class SnapshotCategoryChoices(models.TextChoices):
    NONE = 'none', 'None'
    SCREENING = 'screening', 'Screening'
    OVERVIEW = 'overview', 'Overview'
    SETUP = 'setup', 'Setup'
    TECHNICAL = 'technical', 'Technical'
    FUNDAMENTAL = 'fundamental', 'Fundamental'
    BULL_FLAG = 'bull flag', 'Bull Flag'



# Screening
class SnapshotScreening(TimescaleModel):
    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.CASCADE)
    time = models.DateField()
    screening = models.ForeignKey(Screening, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'snapshot_screening'
        indexes = [
            models.Index(fields=['symbol','time','screening']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['symbol', 'time', 'screening'],
                name='snapshot_screening_unique_symbol_time_screening_pk')
        ]

    def __str__(self):
        return f"Snapshot Screening: {self.symbol.symbol} - {self.screening.name} at {self.time}"


# Overview
class SnapshotOverview(TimescaleModel):
    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.DO_NOTHING)
    time = models.DateField()

    name = models.CharField(max_length=255)

    # Rating
    setup_rating = models.FloatField(null=True, blank=True)
    technical_rating = models.FloatField(null=True, blank=True)
    fundamental_rating = models.FloatField(null=True, blank=True)
    relative_strength = models.FloatField(null=True, blank=True)

    # Performance
    one_month_performance = models.FloatField(null=True, blank=True)
    three_month_performance = models.FloatField(null=True, blank=True)
    six_month_performance = models.FloatField(null=True, blank=True)

    # P/E Liquidity
    percent_change = models.FloatField(null=True, blank=True)
    price_earnings = models.FloatField(null=True, blank=True)
    market_cap = models.FloatField(null=True, blank=True)
    avg_volume_50 = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'snapshot_overview'
        indexes = [
            models.Index(fields=['symbol','time']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['symbol', 'time'],
                name='snapshot_overview_unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"Snapshot Overview: {self.symbol.symbol} - {self.name} at {self.time}"

# Setup
class SnapshotSetup(TimescaleModel):
    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.CASCADE)
    time = models.DateField()

    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    high_52_week = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    weekly_support = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    GICS_sector = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'snapshot_setup'
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='snapshot_setup_unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"Snapshot Step: {self.symbol.symbol} at {self.time}"

# Technical
class SnapshotTechnical(TimescaleModel):
    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.CASCADE)
    time = models.DateField()
    # Data
    lower_bollinger_band = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    upper_bollinger_band = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    RSI_14 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    MACD_12_26_9 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    ADX_14 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    asset_turnover = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    daily_effective_ratio = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'snapshot_technical'
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='snapshot_technical_unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"Snapshot Technical: {self.symbol.symbol} at {self.time}"

# Fundamental
class SnapshotFundamental(TimescaleModel):
    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.CASCADE)
    time = models.DateField()
    # Data
    valuation_rating = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    price_FCF = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    PEG_next_year = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    growth_rating = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    EPS_growth_Q2Q = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    profitability_rating = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    high_growth_momentum_rating = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    avg_ROIC_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    FCF_margin = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    health_rating = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    interest_coverage = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    shares_outstanding_5y_change = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'snapshot_fundamental'
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='snapshot_fundamental_unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"Snapshot Fundamental: {self.symbol.symbol} at {self.time}"

# Bull Flag
class SnapshotBullFlag(TimescaleModel):
    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.CASCADE)
    time = models.DateField()

    # Data
    # Bull Flag
    bull_indicator = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    bull_flag = models.BooleanField(null=True, blank=True)
    weekly_bull_flag = models.BooleanField(null=True, blank=True)
    bullish_engulfing_daily = models.BooleanField(null=True, blank=True)
    bullish_hammer_daily = models.BooleanField(null=True, blank=True)
    bullish_harami_daily = models.BooleanField(null=True, blank=True)
    bullish_engulfing_weekly = models.BooleanField(null=True, blank=True)
    bullish_hammer_weekly = models.BooleanField(null=True, blank=True)
    bullish_harami_weekly = models.BooleanField(null=True, blank=True)
    # Flag
    flag_type = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    flag_pole = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    flag_length = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    flag_width = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    weekly_flag_type = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'snapshot_bull_flag'
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='snapshot_bull_flag_unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"Snapshot Bull Flag: {self.symbol.symbol} at {self.time}"



class SnapshotIndicator(models.Model):
    # Primary Key
    snapshot_indicator_id = models.AutoField(primary_key=True)
    # Foreign Keys
    snapshot_category = models.CharField(max_length=50, choices=SnapshotCategoryChoices.choices, default=SnapshotCategoryChoices.NONE, null=True, blank=True)
    # Data
    snapshot_column = models.CharField(max_length=100)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'snapshot_indicator'

    def __str__(self):
        return f"Snapshot Indicator: {self.name} ({self.snapshot_category})"



