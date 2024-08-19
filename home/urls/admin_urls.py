from home import views
from django.urls import path


urlpatterns = [
    # Pages -> Accounts
    path('settings/', views.admin.settings, name="settings"),
    path('settings/fundamental-company-info-fetching/',
         views.admin.settings_fundamental_company_info_fetching,
         name="settings_fundamental_company_info_fetching"),
]
