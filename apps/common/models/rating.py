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


