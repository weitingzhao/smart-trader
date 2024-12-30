"""django_embed URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from bokeh_django import autoload, directory, document, static_extensions

from . import views
#
#
# urlpatterns = [
#     path(r"", views.index, name="index"),
#     path("shapes/", views.shapes, name="shapes"),
#     path("shapes/<str:arg1>/<str:arg2>", views.shapes_with_args, name="shapes_with_args"),
#     # *static_extensions(),
#     # *staticfiles_urlpatterns(),
# ]
#
# base_path = settings.BASE_DIR
# apps_path = base_path / "apps/bokehs/app"
#
# bokeh_apps = [
#     *directory(apps_path),
#     document("shape_viewer", views.shape_viewer_handler),
#     autoload("shapes_with_args", views.shape_viewer_handler),
#     autoload(r"bokeh/shapes/(?P<arg1>[\w_\-]+)/(?P<arg2>[\w_\-]+)", views.shape_viewer_handler_with_args),
# ]