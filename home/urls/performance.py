from django.urls import path
from home.views import performance

#all below path with [performance]
urlpatterns = [

    ####### performance.calendar_view #######
    # Calendar View -> Default
    path(
        'calendar_view/',
        performance.calendar_view.default,
        name='calendar_view'),

    ####### performance.daily_logs #######
    # Daily Logs -> Default
    path(
        'daily_logs/',
        performance.daily_logs.default,
        name='daily_logs'),

    ####### performance.portfolio_performance #######
    # Portfolio Performance -> Default
    path(
        'portfolio_performance/',
        performance.portfolio_performance.default,
        name='portfolio_performance'),

    ####### performance.trade_history #######
    # Trade History -> Default
    path(
        'trade_history/',
        performance.trade_history.default,
        name='trade_history'),
]