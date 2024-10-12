from django.db import models

class ResearchStockVolume(models.Model):
    symbol = models.ForeignKey(
        'MarketSymbol',
        related_name='research_stock_volume',
        db_column='symbol',
        on_delete=models.DO_NOTHING
    )
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