import re
from datetime import datetime as dt
from apps.common.models import *
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget


class SnapshotOverviewResource(resources.ModelResource):

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

    symbol = fields.Field( column_name='Symbol', attribute='symbol',
        widget=ForeignKeyWidget(MarketSymbol, 'symbol') )
    name = fields.Field(column_name='Name', attribute='name')

    # Rating
    setup_rating = fields.Field(column_name='ChartMill Setup Rating', attribute='setup_rating')
    technical_rating = fields.Field(column_name='ChartMill Technical Rating', attribute='technical_rating')
    fundamental_rating = fields.Field(column_name='ChartMill Fundamental Rating', attribute='fundamental_rating')
    relative_strength = fields.Field(column_name='ChartMill Relative Strength', attribute='relative_strength')

    # Performance
    one_month_performance = fields.Field(column_name='1 Month Performance', attribute='one_month_performance')
    three_month_performance = fields.Field(column_name='3 Month Performance', attribute='three_month_performance')
    six_month_performance = fields.Field(column_name='6 Month Performance', attribute='six_month_performance')

    # P/E Liquidity
    percent_change = fields.Field(column_name='% Change', attribute='percent_change')
    price_earnings = fields.Field(column_name='Price/Earnings', attribute='price_earnings')
    market_cap = fields.Field(column_name='Market Cap', attribute='market_cap')
    avg_volume_50 = fields.Field(column_name='Avg Volume(50)', attribute='avg_volume_50')

    class Meta:
        model = SnapshotOverview
        fields = (
            'id', 'symbol', 'time', 'name',
            # Rating
            'setup_rating', 'technical_rating',  'fundamental_rating', 'relative_strength',
            # Performance
            'one_month_performance', 'three_month_performance', 'six_month_performance',
            # P/E Liquidity
             'percent_change', 'price_earnings', 'market_cap', 'avg_volume_50',
        )
        name = 'SnapshotOverview'

