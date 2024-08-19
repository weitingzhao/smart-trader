from django.urls import include, path
from home import views

urlpatterns = [
    path('', include('home.urls.main_urls')),
    path('accounts/', include('home.urls.accounts_urls')),
    path('admin/', include('home.urls.admin_urls')),

    # Error
    path('error/404/', views.accounts.error_404, name="error_404"),
    path('error/500/', views.accounts.error_500, name="error_500"),
    #logout
    path('logout/', views.account.logout_view, name='logout'),
]
