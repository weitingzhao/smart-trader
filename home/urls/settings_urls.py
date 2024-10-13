from home import views
from django.urls import path
from home.views import settings

#all below path with [settings]
urlpatterns = [

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
