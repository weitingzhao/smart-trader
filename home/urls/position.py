from django.urls import path
from home.views import position

#all below path with [position]
urlpatterns = [

    ####### position.open_positions #######
    # Open Positions -> Portfolio -> List
    path(
        '',
        position.open_positions.get_portfolios,
        name='portfolios'),
    # Open Positions -> Portfolio -> Detail
    path(
        '<int:pk>/',
        position.open_positions.portfolio_detail,
        name='portfolio_detail'),
    # Open Positions -> Portfolio -> Add
    path(
        'add/',
        position.open_positions.add_portfolio,
        name='add_portfolio'),


    # Open Positions -> Holding -> Add
    path(
        '<int:pk>/add_item/',
        position.open_positions.add_portfolio_item,
        name='add_portfolio_item'),


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

    ####### position.close_position #######

]