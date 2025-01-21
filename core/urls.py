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

from bokeh_django import autoload, directory, document
from apps.bokeh import views as bokeh_views

handler404 = 'home.views.accounts.error_404'
handler500 = 'home.views.accounts.error_500'


urlpatterns = ([
    # API
    path("api/", include("apps.api.urls")),
    # Main
    path('', include('home.urls')),
    # Admin
    path('admin/', admin.site.urls),
    # Notifications
    path('inbox/notifications/', include('apps.notifications.urls', namespace='notifications')),
    # Tasks
    path('tasks/', include('apps.tasks.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
urlpatterns += i18n_patterns( path('i18n/', views.main.i18n_view, name="i18n_view"))

if not DEBUG:
    urlpatterns += debug_toolbar_urls()

# Bokeh
# Bokeh autoload js
base_path = settings.BASE_DIR
apps_path = base_path / "apps/bokeh/app"

urlpatterns +=([
    # Below all sample
    path(r"bokeh/", bokeh_views.index, name="bokeh_index"),
    path("bokeh/shapes/", bokeh_views.shapes, name="bokeh_shapes"),
    path("bokeh/shapes/<str:arg1>/<str:arg2>", bokeh_views.shapes_with_args, name="bokeh_shapes_with_args"),
    path("bokeh/sea-surface-temp", bokeh_views.sea_surface),
    path("bokeh/my-sea-surface", bokeh_views.sea_surface_custom_uri),
    path("bokeh/shapes/<str:arg1>/<str:arg2>", bokeh_views.shapes_with_args),
    # *static_extensions(),
    # *staticfiles_urlpatterns(),
])

bokeh_apps = [
    autoload(r"analytics/strategy/test/(?P<data>[\w_\-=%]+)", views.analytics.strategy_analysis.test_result),
    autoload(r"analytics/strategy_optimize/(?P<symbol>[\w_\-]+)/(?P<cut_over>[\w_\-]+)",
             views.analytics.strategy_optimize.bokeh_optimize),

    #below all sample
    *directory(apps_path),

    document("bokeh/sea_surface_direct", bokeh_views.sea_surface_handler),
    document("bokeh/sea_surface_with_template", bokeh_views.sea_surface_handler_with_template),
    document("bokeh/sea_surface_bokeh", apps_path / "sea_surface.py"),
    document("bokeh/shape_viewer", bokeh_views.shape_viewer_handler),
    autoload("bokeh/sea-surface-temp", bokeh_views.sea_surface_handler),
    autoload("bokeh/sea_surface_custom_uri", bokeh_views.sea_surface_handler),
    autoload("bokeh/shapes/", bokeh_views.shape_viewer_handler),
    autoload(r"bokeh/shapes/(?P<arg1>[\w_\-]+)/(?P<arg2>[\w_\-]+)", bokeh_views.shape_viewer_handler_with_args),
]


# from bokeh.plotting import figure, curdoc
# from bokeh.models import ColumnDataSource
# import redis
# import threading
# import json
#
#
# # Data source
# source = ColumnDataSource(data={'x': [], 'y': []})
#
# # Create Bokeh plot
# plot = figure(title="Dynamic Plot", x_axis_label="x", y_axis_label="y")
# plot.line('x', 'y', source=source)
#
# def update_plot(data):
#     source.stream(data)
#
# def redis_listener():
#     redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
#     pubsub = redis_client.pubsub()
#     pubsub.subscribe("bokeh_plot_channel")
#
#     for message in pubsub.listen():
#         if message['type'] == 'message':
#             data = json.loads(message['data'])
#             curdoc().add_next_tick_callback(lambda: update_plot(data))
#
# # Start Redis listener in a separate thread
# thread = threading.Thread(target=redis_listener)
# thread.daemon = True
# thread.start()
#
# # Add the plot to the Bokeh document
# curdoc().add_root(plot)