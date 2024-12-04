from . import Wishlist
from django.db import models
from .market import MarketSymbol
from import_export_celery.models import ImportJob
from timescale.db.models.models import TimescaleModel


class ScreeningChoices(models.TextChoices):
    NONE        = '0', 'None'
    Active        = '1', 'Active'
    Deactivate = '-1', 'Deactivate'

class ScreeningOperationChoices(models.TextChoices):
    NONE              = '0', 'None'
    BYPASS          = '-1', 'Bypass'
    QUEUE            = '1', 'Queue'
    PROCESSING  = '2', 'Processing'
    Done               = '4', 'Done'
    FAILED            = '5', 'Failed'


class Screening(models.Model):

    # Primary Key
    screening_id = models.AutoField(primary_key=True)

    # Reference to self
    ref_screening = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    addendum_screening = models.ForeignKey('self', related_name='addendums', on_delete=models.SET_NULL, null=True, blank=True)

    # Status
    status = models.CharField(max_length=8, choices=ScreeningChoices.choices, default=ScreeningChoices.NONE, null=True, blank=True)

    # Screening Details
    name = models.CharField(max_length=255)
    description = models.TextField()
    source = models.CharField(max_length=255, null=True, blank=True)
    file_pattern = models.CharField(max_length=255, null=True, blank=True)
    celery_models = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'screening'

    def __str__(self):
        return f"Screening: {self.name}"


class ScreeningOperation(TimescaleModel):

    # Primary Key
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField()
    file_name = models.CharField(max_length=255)

    # Status
    status = models.CharField(max_length=8, choices=ScreeningOperationChoices.choices, default=ScreeningOperationChoices.NONE, null=True, blank=True)

    screening = models.ForeignKey(Screening, on_delete=models.DO_NOTHING, null=True, blank=True)
    import_job = models.ForeignKey(ImportJob, on_delete=models.DO_NOTHING, null=True, blank=True)

    processed_at = models.DateTimeField(null=True, blank=True)
    processed_result = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'screening_operation'
        indexes = [
            models.Index(fields=['file_name', 'time']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['time', 'file_name'], name='screening_operation_unique_time_file_name')
        ]

    def __str__(self):
        return f"Screening Operation: {self.screening.name} at {self.time}"



class ScreeningResult(models.Model):

    # Primary Key
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

    # Primary Key
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
