from django.db import models

from apps.common.models import MarketSymbol


class ResearchStockVolume(models.Model):
    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.DO_NOTHING)
    volume = models.BigIntegerField(null=True, blank=True)
    avg_volume_50 = models.BigIntegerField(null=True, blank=True)
    avg_volume_5 = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'research_stock_volume'
        constraints = [
            models.UniqueConstraint(fields=['symbol'], name='unique_symbol')
        ]

    def __str__(self):
        return f"research.stock_volume: {self.symbol}"
