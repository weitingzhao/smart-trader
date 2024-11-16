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

    # wire
    path('funding/create/', cash_flow.cash_overview.add_funding, name='add_funding'),
    path('funding/<int:funding_id>/', cash_flow.cash_overview.get_funding, name='get_funding'),
    path('funding/<int:funding_id>/edit/', cash_flow.cash_overview.edit_funding, name='edit_funding'),
    path('funding/<int:funding_id>/delete/', cash_flow.cash_overview.delete_funding, name='delete_funding'),

    path('balance/create/', cash_flow.cash_overview.add_cash_balance, name='add_cash_balance'),
    path('balance/<int:balance_id>/', cash_flow.cash_overview.get_cash_balance, name='get_cash_balance'),
    path('balance/<int:balance_id>/edit/', cash_flow.cash_overview.edit_cash_balance, name='edit_cash_balance'),
    path('balance/<int:balance_id>/delete/', cash_flow.cash_overview.delete_cash_balance, name='delete_cash_balance'),

    ####### cash_flow.cash_flow_history #######
    # Saved Screeners -> Default
    path(
        'cash_flow_history/',
        cash_flow.cash_flow_history.default,
        name='cash_flow_history'),



]