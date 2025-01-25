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

    path(
        'stock_live_price_ws/',
        settings.account_settings.stock_live_price_ws,
        name='stock_live_price_ws'),

    # Account Settings -> Add Portfolio
    path(
        'portfolio/add/',
        settings.account_settings.add_portfolio,
        name='account_add_portfolio'),
    # Account Settings -> Edit Portfolio
    path(
        'portfolio/edit/',
        settings.account_settings.edit_portfolio,
        name='account_edit_portfolio'),
    # Account Settings -> Delete Default Portfolio
    path(
        'portfolio/delete/',
        settings.account_settings.delete_portfolio,
        name='account_delete_portfolio'),
    # Account Settings -> Toggle Default Portfolio
    path(
        'portfolio/toggle_default/',
        settings.account_settings.toggle_default_portfolio,
        name='account_toggle_default_portfolio'),


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
