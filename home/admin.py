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

admin.site.register(UtilitiesLookup, UtilitiesLookupAdmin)

