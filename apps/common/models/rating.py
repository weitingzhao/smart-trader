from django.db import models
from apps.common.models import *

class Rating(TimescaleModel):

    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.CASCADE)
    time = models.DateField()
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    # Data
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'rating'
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time', 'strategy'], name='rating_unique_symbol_time_strategy_pk')
        ]

    def __str__(self):
        return f"Rating: {self.symbol.symbol} - {self.strategy.name} at {self.time}"



class RatingIndicatorResult(TimescaleModel):

    # Primary Key
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.DO_NOTHING)
    time = models.DateField()

    sma = models.FloatField(null=True, blank=True)
    rsi = models.FloatField(null=True, blank=True)
    bollinger_upper = models.FloatField(null=True, blank=True)
    bollinger_lower = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'rating_indicator_result'
        indexes = [
            models.Index(fields=['symbol', 'time']),
        ]
        # Setting a composite primary key
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='rating_indicator_result_unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"screening.rating_indicator_result: {self.symbol} on {self.time}"



