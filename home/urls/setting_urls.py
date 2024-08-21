from home import views
from django.urls import path

#all below path with admin/setting/...
urlpatterns = [

    # Dashboard -> Settings
    path('', views.setting.settings, name="settings"),

    # Dashboard -> Settings -> Data -> Fundamentals
    path('fetching/symbols/', views.setting.fetching_symbol, name='settings_fetching_symbol'),
    path('indexing/symbols/', views.setting.indexing_symbol, name='settings_indexing_symbol'),
    path('fetching/company-info/', views.setting.fetching_company_info, name="settings_fetching_company_info"),

]
