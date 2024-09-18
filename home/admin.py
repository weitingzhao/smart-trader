from django.contrib import admin
from django import forms

# Register your models here.
from apps.common.models import *




class UtilitiesLookupAdmin(admin.ModelAdmin):
    list_display = ('category', 'type', 'order', 'key', 'value')
    list_filter = ('category', 'type')

    actions = ['delete_selected']
    ordering = ('category', 'type', 'order')
    search_fields = ('category', 'type','key', 'value')

class UtilitiesFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'key', 'value')
    list_filter = ('name',)

    actions = ['delete_selected']
    ordering = ('name', 'order', 'key', 'value')
    search_fields = ('name', 'key','value')

admin.site.register(UtilitiesLookup, UtilitiesLookupAdmin)
admin.site.register(UtilitiesFilter, UtilitiesFilterAdmin)

