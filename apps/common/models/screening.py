import re
from datetime import datetime as dt
from django.db import models
from . import Wishlist
from .market import MarketSymbol
from timescale.db.models.models import TimescaleModel

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget


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
            models.UniqueConstraint(fields=['symbol', 'time'], name='unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"screening.rating_indicator_result: {self.symbol} on {self.time}"

#///////////////// snapshot //////////////////////

class ScreeningSnapshotOverview(TimescaleModel):

    symbol = models.ForeignKey(MarketSymbol, to_field='symbol', on_delete=models.DO_NOTHING)
    time = models.DateField()

    name = models.CharField(max_length=255)

    #rating
    setup_rating = models.FloatField(null=True, blank=True)
    technical_rating = models.FloatField(null=True, blank=True)
    fundamental_rating = models.FloatField(null=True, blank=True)

    relative_strength = models.FloatField(null=True, blank=True)
    percent_change = models.FloatField(null=True, blank=True)

    one_month_performance = models.FloatField(null=True, blank=True)
    three_month_performance = models.FloatField(null=True, blank=True)
    six_month_performance = models.FloatField(null=True, blank=True)

    price_earnings = models.FloatField(null=True, blank=True)
    market_cap = models.FloatField(null=True, blank=True)
    avg_volume_50 = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'screening_snapshot_overview'
        indexes = [
            models.Index(fields=['symbol','time']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['symbol', 'time'], name='snapshot_overview_unique_symbol_time_pk')
        ]

    def __str__(self):
        return f"Screening Snapshot Overview: {self.symbol.symbol} - {self.name} at {self.time}"


class ScreeningSnapshotOverviewResource(resources.ModelResource):

    def before_import(self, dataset, **kwargs):
        try:
            filename = kwargs['file_name']
            match = re.search(r'_(\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2}\.\d{3}Z)\.csv$', filename)
            if match:
                date_str = match.group(1)
                self.date_obj = dt.strptime(date_str, '%Y-%m-%dT%H_%M_%S.%fZ').date()
        except KeyError:
            try:
                filename = self.import_job.file.name
                match = re.search(r'_(\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2})_', filename)
                if match:
                    date_str = match.group(1)
                    self.date_obj = dt.strptime(date_str, '%Y-%m-%dT%H_%M_%S').date()
            except AttributeError:
                self.date_obj = None


    def before_import_row(self, row, **kwargs):
        for key, value in row.items():
            if value == "N/A":
                row[key] = None
        if self.date_obj:
            row['time'] = self.date_obj
            # print(f"row - Date===========>: {row['time']}")


    # def before_save_instance(self, instance, using_transactions, dry_run, **kwargs):
    #     if not instance.symbol:
    #         raise ValueError(f"Symbol '{instance.symbol}' not found in MarketSymbol table.")

    # def skip_row(self, instance, original, dry_run, **kwargs):
    #     return not MarketSymbol.objects.filter(symbol=instance.symbol).exists()

    symbol = fields.Field(
        column_name='Symbol',
        attribute='symbol',
        widget=ForeignKeyWidget(MarketSymbol, 'symbol')
    )
    name = fields.Field(column_name='Name', attribute='name')

    setup_rating = fields.Field(column_name='ChartMill Setup Rating', attribute='setup_rating')
    technical_rating = fields.Field(column_name='ChartMill Technical Rating', attribute='technical_rating')
    fundamental_rating = fields.Field(column_name='ChartMill Fundamental Rating', attribute='fundamental_rating')

    relative_strength = fields.Field(column_name='ChartMill Relative Strength', attribute='relative_strength')
    percent_change = fields.Field(column_name='% Change', attribute='percent_change')

    one_month_performance = fields.Field(column_name='1 Month Performance', attribute='one_month_performance')
    three_month_performance = fields.Field(column_name='3 Month Performance', attribute='three_month_performance')
    six_month_performance = fields.Field(column_name='6 Month Performance', attribute='six_month_performance')

    price_earnings = fields.Field(column_name='Price/Earnings', attribute='price_earnings')
    market_cap = fields.Field(column_name='Market Cap', attribute='market_cap')
    avg_volume_50 = fields.Field(column_name='Avg Volume(50)', attribute='avg_volume_50')

    class Meta:
        model = ScreeningSnapshotOverview
        fields = (
            'id', 'symbol', 'time', 'name',

            'setup_rating', 'technical_rating',
            'fundamental_rating', 'relative_strength', 'percent_change',

            'one_month_performance', 'three_month_performance', 'six_month_performance',

            'price_earnings', 'market_cap', 'avg_volume_50',
        )
        name = 'ScreeningSnapshotOverview'

