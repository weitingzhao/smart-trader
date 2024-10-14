from django.urls import path
from home.views import cash_flow

#all below path with [cash_flow]
urlpatterns = [

    ####### cash_flow.cash_overview #######
    # Wishlist Overview -> Default
    path(
        'cash_overview/',
        cash_flow.cash_overview.default,
        name='cash_overview'),

    ####### cash_flow.cash_flow_history #######
    # Saved Screeners -> Default
    path(
        'cash_flow_history/',
        cash_flow.cash_flow_history.default,
        name='cash_flow_history'),

]