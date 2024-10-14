from django.urls import path
from home.views import dashboard as dashboard

#all below path with [screening]
urlpatterns = [

    ####### dashboard.overview #######
    # Overview -> Default
    path(
        'overview/',
        dashboard.overview.default,
        name='dashboard_overview'),

    ####### dashboard.market_summary #######
    # Overview -> Default
    path(
        'market_summary/',
        dashboard.market_summary.default,
        name='dashboard_market_summary'),

    ####### dashboard.recent_activity #######
    # Overview -> Default
    path(
        'recent_activity/',
        dashboard.recent_activity.default,
        name='dashboard_recent_activity'),

]