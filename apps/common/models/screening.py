from django.db import models

from . import Wishlist
from .market import MarketSymbol

class Screening(models.Model):
    """
    This model is used to store the screening strategy
    """
    screening_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        db_table = 'screening'

    def __str__(self):
        return f"Screening: {self.name}"



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

