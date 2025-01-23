from django.db import models
from apps.common.models import *
from timescale.db.models.models import TimescaleModel

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _  # Django 4.0.0 and more
from ..fields import ImportExportFileField


class ScreeningChoices(models.TextChoices):
    NONE        = '0', 'None'
    Active        = '1', 'Active'
    Deactivate = '-1', 'Deactivate'

class ScreeningOperationChoices(models.TextChoices):
    NONE              = '0', 'None'
    BYPASS          = '-1', 'Bypass'
    QUEUE            = '1', 'Queue'
    DONE               = '4', 'Done'
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
    import_models = models.CharField(max_length=255, null=True, blank=True)

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

    change_summary = ImportExportFileField(
        verbose_name=_("Summary of changes made by this import"),
        upload_to="django-import-export-celery-import-change-summaries",
        blank=True,
        null=True,
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_result = models.TextField(null=True, blank=True)
    errors = models.TextField(null=True, blank=True)

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

# class ScreeningResult(models.Model):
#
#     # Primary Key
#     screening_result_id = models.AutoField(primary_key=True)
#
#     screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
#     symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
#     wishlist = models.ForeignKey(Wishlist, on_delete=models.DO_NOTHING, null=True, blank=True)
#     run_at = models.DateTimeField()
#
#     class Meta:
#         db_table = 'screening_result'
#
#     def __str__(self):
#         return f"Screening Result: {self.screening.name} for {self.symbol.symbol} at {self.run_at}"
#
# class ScreeningCriteria(models.Model):
#
#     # Primary Key
#     screener_id = models.AutoField(primary_key=True)
#
#     screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
#     criteria = models.CharField(max_length=255)
#     condition = models.CharField(max_length=255)
#     explain = models.TextField()
#
#     class Meta:
#         db_table = 'screening_criteria'
#
#     def __str__(self):
#         return f"Screening Criteria: {self.criteria} for {self.screening.name}"


