from django.contrib import admin
from django import forms

# Register your models here.
from apps.common.models import *
from apps.common.resources import *
from import_export.admin import ImportExportMixin, ImportMixin, ImportExportModelAdmin


# from import_export_celery.admin_actions import create_export_job_action

class UtilitiesLookupAdmin(admin.ModelAdmin):
    list_display = ('category', 'type', 'order', 'key', 'value')
    list_filter = ('category', 'type')

    actions = ['delete_selected']
    ordering = ('category', 'type', 'order')
    search_fields = ('category', 'type','key', 'value')
admin.site.register(UtilitiesLookup, UtilitiesLookupAdmin)

class UtilitiesFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'key', 'value')
    list_filter = ('name',)

    actions = ['delete_selected']
    ordering = ('name', 'order', 'key', 'value')
    search_fields = ('name', 'key','value')
admin.site.register(UtilitiesFilter, UtilitiesFilterAdmin)


class ScreeningAdmin(admin.ModelAdmin):
    list_display = (
        'screening_id', 'name', 'status',  'ref_screening',
        'addendum_screening', 'file_pattern',
        'celery_models', 'source', 'description')
    list_filter = ('description', 'status', 'celery_models')

    actions = ['delete_selected']
    ordering = ('screening_id', 'name', 'ref_screening', 'addendum_screening', 'file_pattern', 'source')
    search_fields = ('name',)
admin.site.register(Screening, ScreeningAdmin)


@admin.register(SnapshotScreening)
class SnapshotScreeningAdmin(ImportExportModelAdmin):
    list_display = ("symbol","time")
    resource_classes = [SnapshotScreeningResource]

@admin.register(SnapshotOverview)
class SnapshotOverviewAdmin(ImportExportModelAdmin):
    list_display = ("symbol","time")
    resource_classes = [SnapshotOverviewResource]


@admin.register(SnapshotTechnical)
class SnapshotTechnicalAdmin(ImportExportModelAdmin):
    list_display = ("symbol","time")
    resource_classes = [SnapshotTechnicalResource]

@admin.register(SnapshotFundamental)
class SnapshotFundamentalAdmin(ImportExportModelAdmin):
    list_display = ("symbol","time")
    resource_classes = [SnapshotFundamentalResource]

@admin.register(SnapshotSetup)
class SnapshotSetupAdmin(ImportExportModelAdmin):
    list_display = ("symbol","time")
    resource_classes = [SnapshotSetupResource]

@admin.register(SnapshotBullFlag)
class SnapshotBullFlagAdmin(ImportExportModelAdmin):
    list_display = ("symbol","time")
    resource_classes = [SnapshotBullFlagResource]


# @admin.register(ScreeningChartmillOverview)
# class Celery_ScreeningChartmillOverviewAdmin(ImportMixin, admin.ModelAdmin):
#     list_display = ("name",)
#     resource = ScreeningChartmillOverviewResource()
#     resource_classes = [ScreeningChartmillOverviewResource]
#     actions = (create_export_job_action,)