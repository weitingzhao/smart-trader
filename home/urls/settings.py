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
        'overview/',
        settings.risk_preferences.default,
        name='risk_preferences'),

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

    # Admin Panel -> Customize
    path(
        'customize/',
        settings.admin_panel.customize,
        name='customize'),
    path(
        'customize/position_sizing',
        settings.admin_panel.customize_position_sizing,
        name='customize_position_sizing'),

    # Admin Panel -> Lookup
    path(
        'lookup/',
        settings.admin_panel.lookup_page,
        name='lookup'),
]
