from django.db import models
from apps.common.models import *
from django.contrib.auth.models import User


class StrategyCategoryChoices(models.TextChoices):
    NONE              = 'None', 'None'
    VCP                 = 'vcp', 'VCP'
    SCREENING       = 'screening', 'Screening'
    OVERVIEW        = 'overview', 'Overview'
    SETUP               = 'setup', 'Setup'
    TECHNICAL       = 'technical', 'Technical'
    FUNDAMENTAL = 'fundamental', 'Fundamental'
    BULL_FLAG       = 'bull flag', 'Bull Flag'

class Strategy(models.Model):

    # Primary Key
    strategy_id = models.AutoField(primary_key=True)
    # Foreign Keys
    owner_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    # Data
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=50, null=True, blank=True)  # New field
    description = models.TextField()
    as_of_date = models.DateField()
    custom_order = models.IntegerField(default=0)  # New field

    class Meta:
        db_table = 'strategy'

    def __str__(self):
        return f"Strategy: {self.name} by {self.owner_user.username}"


class StrategyCategory(models.Model):

    # Primary Key
    strategy_category_id = models.AutoField(primary_key=True)
    # Foreign Keys
    strategy = models.ForeignKey(Strategy, on_delete=models.DO_NOTHING, null=True, blank=True)
    # Data
    strategy_category = models.CharField(max_length=50, choices=StrategyCategoryChoices.choices, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'strategy_category'

    def __str__(self):
        return f"Strategy Category: {self.strategy_category} for Strategy ID {self.strategy_id}"


class StrategyCategorySnapshot(models.Model):

    # Primary Key
    strategy_category_snapshot_id = models.AutoField(primary_key=True)
    # Foreign Keys
    strategy_category = models.ForeignKey(StrategyCategory, on_delete=models.CASCADE)
    snapshot_indicator = models.ForeignKey(SnapshotIndicator, on_delete=models.CASCADE)
    # Data
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'strategy_category_snapshot'

    def __str__(self):
        return f"Strategy Category Snapshot: {self.strategy_category_id} - {self.snapshot_indicator_id}"


class StrategyAlgoScript(models.Model):

    # Primary Key
    strategy_algo_script_id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=50)
    text = models.TextField(null=True)

    class Meta:
        db_table = 'strategy_algo_script'

    def __str__(self):
        return f"Strategy Algo Script:  {self.title}"


