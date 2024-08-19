"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from core.settings import DEBUG
from home import views
from django.views.static import serve
from debug_toolbar.toolbar import debug_toolbar_urls

handler404 = 'home.views.accounts.error_404'
handler500 = 'home.views.accounts.error_500'

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),

    # Notifications
    # path('inbox/notifications/', include('apps.notifications.urls', namespace='notifications')),

    path('tasks/', include('apps.tasks.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(
    path('i18n/', views.common.i18n_view, name="i18n_view")
)

if not DEBUG:
    urlpatterns += debug_toolbar_urls()