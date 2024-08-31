from django.urls import include, path
from home import views

urlpatterns = [
    # Main
    path('', include('home.urls.main_urls')),

    # Admin
    path('accounts/', include('home.urls.accounts_urls')),
    path('settings/', include('home.urls.setting_urls')),

    # Portfolio
    path('portfolio/', include('home.urls.portfolio_urls')),

    # Error
    path('error/404/', views.accounts.error_404, name="error_404"),
    path('error/500/', views.accounts.error_500, name="error_500"),

    #logout
    path('logout/', views.account.logout_view, name='logout'),
]
