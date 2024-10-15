from django.urls import path
from home.views import settings

#all below path with [settings]
urlpatterns = [

    ####### settings.account_settings #######
    # Account Settings -> Default
    path(
        'account_settings/',
        settings.account_settings.default,
        name='account_settings'),

    ####### settings.risk_references #######
    # Risk References -> Default
    path(
        'risk/',
        settings.risk_preferences.default,
        name='risk_preferences'),
    path(
        'risk/static_risk',
        settings.risk_preferences.settings_risk_static_risk,
        name='settings_risk_static_risk'),

    ####### settings.notifications #######
    # Overview -> Default
    path(
        'notifications/',
        settings.notifications.default,
        name='notifications'),



    # Admin Panel -> Settings
    path(
        'settings',
        settings.admin_panel.settings,
        name="settings"),

    # Admin Panel -> Lookup
    path(
        'lookup/',
        settings.admin_panel.lookup_page,
        name='lookup'),
]
