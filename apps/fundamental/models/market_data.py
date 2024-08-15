from django.db import models
from timescale.db.models.models import TimescaleModel


class MarketSymbol(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    market = models.CharField(max_length=50)
    asset_type = models.CharField(max_length=50)
    ipo_date = models.DateField(null=True, blank=True)
    delisting_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'market_symbol'

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class MarketStockHistoricalBars(TimescaleModel):
    symbol = models.CharField(max_length=10, null=False, blank=False, default="NaN")
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    trade_count = models.FloatField()
    volume_weighted_average_price = models.FloatField()

    class Meta:
        db_table = 'market_stock_hist_bars_ts'
        indexes = [
            models.Index(fields=['symbol', 'time']),
        ]
        # Setting a composite primary key
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='symbol_timestamp_pk'),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.time}"



