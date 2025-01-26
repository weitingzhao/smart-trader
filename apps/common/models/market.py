from django.db import models
from timescale.db.models.models import TimescaleModel


class MarketSymbol(models.Model):
    symbol = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    market = models.CharField(max_length=50)
    asset_type = models.CharField(max_length=50)
    ipo_date = models.DateField(null=True, blank=True)
    delisting_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20)
    has_company_info = models.BooleanField(default=False)
    is_delisted = models.BooleanField(default=False)
    min_period_yfinance = models.CharField(max_length=20, blank=True)
    daily_period_yfinance = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'market_symbol'

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class MarketStockHistoricalBarsByMin(TimescaleModel):
    symbol = models.CharField(max_length=10, null=False, blank=False, default="NaN")
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    dividend = models.FloatField()
    stock_splits = models.FloatField()

    class Meta:
        db_table = 'market_stock_hist_bars_min_ts'
        indexes = [
            models.Index(fields=['symbol', 'time']),
        ]
        # Setting a composite primary key
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='symbol_timestamp_min_pk'),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.time}"

class MarketStockHistoricalBarsByDay(TimescaleModel):
    symbol = models.CharField(max_length=10, null=False, blank=False, default="NaN")
    time = models.DateField(null=False, blank=False)  # Changed to DateField'

    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    dividend = models.FloatField()
    stock_splits = models.FloatField()

    class Meta:
        db_table = 'market_stock_hist_bars_day_ts'
        indexes = [
            models.Index(fields=['symbol', 'time']),
        ]
        # Setting a composite primary key
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='symbol_timestamp_day_pk'),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.time}"


class MarketStockHistoricalBarsByHour(TimescaleModel):
    symbol = models.CharField(max_length=10, null=False, blank=False, default="NaN")
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    # dividend = models.FloatField()
    # stock_splits = models.FloatField()

    class Meta:
        db_table = 'market_stock_hist_bars_hour_ts'
        indexes = [
            models.Index(fields=['symbol', 'time']),
        ]
        # Setting a composite primary key
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='symbol_timestamp_hour_pk'),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.time}"

class MarketStockHistoricalBarsByHourExt(TimescaleModel):
    symbol = models.CharField(max_length=10, null=False, blank=False, default="NaN")
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()

    class Meta:
        db_table = 'market_stock_hist_bars_hour_ext_ts'
        indexes = [
            models.Index(fields=['symbol', 'time']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='symbol_timestamp_hour_extended_pk'),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.time}"