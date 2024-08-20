from home import views
from django.urls import path


urlpatterns = [
    # Pages -> Accounts
    path('', views.admin.settings, name="settings"),
    path('fetching/company-info/',
         views.admin.settings_fetching_company_info,
         name="settings_fetching_company_info"),
]
