from django.urls import path
from home.views import position

#all below path with [position]
urlpatterns = [

    ####### position.open_positions #######
    # Open Positions -> Default
    path(
        'open_positions/',
        position.open_positions.default,
        name='open_positions'),

    # Open Positions -> Holding -> Add
    path(
        'holding/<int:pk>/add/',
        position.open_positions.add_holding,
        name='add_holding'),


    # Open Positions -> Transactions -> List
    path(
        '<int:portfolio_id>/item/<int:portfolio_item_id>/transactions/',
        position.open_positions.get_transaction_history,
        name='transactions'),
    # Open Positions -> Transaction -> Add
    path(
        'add/transaction/',
        position.open_positions.add_transaction,
        name='add_transaction'),

    # Open Positions -> Transaction -> Delete
    path(
        'delete/<str:transaction_id>/',
        position.open_positions.delete_transaction,
        name='delete_transaction'),

    ####### position.adjust_stop_limits #######
    # Adjust Stop Limit  -> Default
    path(
        'adjust_stop_limits/',
        position.adjust_stop_limits.default,
        name='adjust_stop_limits'),

    ####### position.close_position #######
    # Close Position  -> Default
    path(
        'close_positions/',
        position.close_positions.default,
        name='close_positions'),

]