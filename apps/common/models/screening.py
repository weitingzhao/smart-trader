from . import Wishlist
from django.db import models
from .market import MarketSymbol
from import_export_celery.models import ImportJob
from timescale.db.models.models import TimescaleModel

class Screening(models.Model):
    """
    This model is used to store the screening strategy
    """
    screening_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    source = models.CharField(max_length=255, null=True, blank=True)
    file_pattern = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'screening'

    def __str__(self):
        return f"Screening: {self.name}"


class ScreeningOperation(TimescaleModel):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField()
    screening = models.ForeignKey(Screening, on_delete=models.DO_NOTHING, null=True, blank=True)
    import_job = models.ForeignKey(ImportJob, on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta:
        db_table = 'screening_operation'
        indexes = [
            models.Index(fields=['screening', 'time']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['screening', 'time'], name='screening_operation_unique_screening_time')

        ]

    def __str__(self):
        return f"Screening Operation: {self.screening.name} at {self.time}"

class ScreeningResult(models.Model):
    """
    This model is used to store the result of a screening strategy
    """
    screening_result_id = models.AutoField(primary_key=True)
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.DO_NOTHING, null=True, blank=True)
    run_at = models.DateTimeField()

    class Meta:
        db_table = 'screening_result'

    def __str__(self):
        return f"Screening Result: {self.screening.name} for {self.symbol.symbol} at {self.run_at}"


class ScreeningCriteria(models.Model):
    """
    This model is used to store the criteria of a screening strategy
    """
    screening_criteria_id = models.AutoField(primary_key=True)
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    criteria = models.CharField(max_length=255)
    condition = models.CharField(max_length=255)
    explain = models.TextField()

    class Meta:
        db_table = 'screening_criteria'

    def __str__(self):
        return f"Screening Criteria: {self.criteria} for {self.screening.name}"


class RatingIndicatorResult(TimescaleModel):

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
