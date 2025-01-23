from django.contrib import admin
from apps.common.resources import *
from import_export.admin import ImportExportMixin, ImportMixin, ImportExportModelAdmin

# Utilities
class UtilitiesLookupAdmin(admin.ModelAdmin):
    list_display = ('category', 'type', 'order', 'key', 'value')
    list_filter = ('category', 'type')
    actions = ['delete_selected']
    ordering = ('category', 'type', 'order')
    search_fields = ('category', 'type','key', 'value')
admin.site.register(UtilitiesLookup, UtilitiesLookupAdmin)

@admin.register(UtilitiesFilter)
class UtilitiesFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'key', 'value')
    list_filter = ('name',)
    actions = ['delete_selected']
    ordering = ('name', 'order', 'key', 'value')
    search_fields = ('name', 'key','value')

# Screenings
@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = (
        'screening_id', 'name', 'status',  'ref_screening',
        'addendum_screening', 'file_pattern',
        'import_models', 'source', 'description')
    list_filter = ('description', 'status', 'import_models')
    actions = ['delete_selected']
    ordering = ('screening_id', 'name', 'ref_screening', 'addendum_screening', 'file_pattern', 'source')
    search_fields = ('name',)

@admin.register(ScreeningOperation)
class ScreeningOperationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'time', 'file_name',  'processed_at', 'status', 'processed_result')
    list_filter = ('time', 'status', 'screening_id')
    actions = ['delete_selected']
    ordering = ('id', 'time', 'status')
    search_fields = ('id','time', 'file_name', 'processed_at', 'status', 'processed_result')

# Snapshots
@admin.register(SnapshotIndicator)
class SnapshotIndicatorAdmin(admin.ModelAdmin):
    list_display = (
        'snapshot_indicator_id', 'name', 'snapshot_category',
        'snapshot_column_group', 'snapshot_column')
    list_filter = ('snapshot_category','snapshot_column_group')
    actions = ['delete_selected']
    ordering = (
        'snapshot_indicator_id', 'name', 'snapshot_category',
        'snapshot_column_group', 'snapshot_column')
    search_fields = ('snapshot_category','snapshot_column_group', 'snapshot_column')

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('strategy_id', 'short_name', 'name', 'custom_order', 'owner_user', 'as_of_date')
    search_fields = ('name', 'owner_user__username')
    list_filter = ('as_of_date',)
    ordering = ('-as_of_date',)

# Snapshots detail tables
# @admin.register(SnapshotScreening)
# class SnapshotScreeningAdmin(ImportExportModelAdmin):
#     list_display = ("symbol","time")
#     resource_classes = [SnapshotScreeningResource]
#
# @admin.register(SnapshotOverview)
# class SnapshotOverviewAdmin(ImportExportModelAdmin):
#     list_display = ("symbol","time")
#     resource_classes = [SnapshotOverviewResource]
#
# @admin.register(SnapshotTechnical)
# class SnapshotTechnicalAdmin(ImportExportModelAdmin):
#     list_display = ("symbol","time")
#     resource_classes = [SnapshotTechnicalResource]
#
# @admin.register(SnapshotFundamental)
# class SnapshotFundamentalAdmin(ImportExportModelAdmin):
#     list_display = ("symbol","time")
#     resource_classes = [SnapshotFundamentalResource]
#
# @admin.register(SnapshotSetup)
# class SnapshotSetupAdmin(ImportExportModelAdmin):
#     list_display = ("symbol","time")
#     resource_classes = [SnapshotSetupResource]
#
# @admin.register(SnapshotBullFlag)
# class SnapshotBullFlagAdmin(ImportExportModelAdmin):
#     list_display = ("symbol","time")
#     resource_classes = [SnapshotBullFlagResource]


# @admin.register(ScreeningChartmillOverview)
# class Celery_ScreeningChartmillOverviewAdmin(ImportMixin, admin.ModelAdmin):
#     list_display = ("name",)
#     resource = ScreeningChartmillOverviewResource()
#     resource_classes = [ScreeningChartmillOverviewResource]
#     actions = (create_export_job_action,)