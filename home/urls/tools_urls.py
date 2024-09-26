from home import views
from django.urls import path

#all below path with admin/setting/...
urlpatterns = [

    # Tools -> Settings
    path('settings', views.tools.settings, name="settings"),

    # Tools -> Customize
    path('customize/', views.tools.customize, name='customize'),
    path('customize/position_sizing', views.tools.customize_position_sizing, name='customize_position_sizing'),

    # Tools -> Lookup
    path('lookup/', views.tools.lookup_page, name='lookup'),
]
