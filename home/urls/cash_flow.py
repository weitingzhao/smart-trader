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

    path('create/', cash_flow.cash_overview.add, name='cash_add_funding'),

    path('<int:funding_id>/', cash_flow.cash_overview.get_funding, name='cash_get_funding'),

    path('<int:funding_id>/edit/', cash_flow.cash_overview.edit_funding, name='cash_edit_funding'),
    path('<int:funding_id>/delete/', cash_flow.cash_overview.delete_funding, name='delete_funding'),

    ####### cash_flow.cash_flow_history #######
    # Saved Screeners -> Default
    path(
        'cash_flow_history/',
        cash_flow.cash_flow_history.default,
        name='cash_flow_history'),



]