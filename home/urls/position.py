from django.urls import path
from home.views import position

#all below path with [position]
urlpatterns = [

    ####### Positions #######
    # Open Positions -> Default
    path('open_positions/',
        position.open_positions.default,
        name='open_positions'),

    ####### holding #######
    path('holding/<int:pk>/add/',
        position.open_positions.add_holding,
        name='add_holding'),

    ####### holding.order #######

    path('holding/buy/order/<int:holding_buy_order_id>/',
        position.open_positions.get_holding_buy_order,
        name='get_holding_buy_order'),

    path('holding/buy/order/<int:holding_buy_order_id>/edit/',
        position.open_positions.edit_holding_buy_order,
        name='edit_holding_buy_order'),

    path('holding/buy/order/<int:holding_buy_order_id>/delete/',
        position.open_positions.delete_holding_buy_order,
        name='delete_holding_sell_order'),

    path('holding/sell/order/<int:holding_sell_order_id>/',
         position.open_positions.get_holding_sell_order,
         name='get_holding_sell_order'),

    path('holding/sell/order/<int:holding_sell_order_id>/edit/',
         position.open_positions.edit_holding_sell_order,
         name='edit_holding_sell_order'),
    path('holding/sell/order/<int:holding_sell_order_id>/delete/',
         position.open_positions.delete_holding_sell_order,
         name='delete_holding_sell_order'),

    ####### holding.action #######

    path('holding/buy/action/<int:holding_buy_order_id>/add/',
        position.open_positions.add_holding_buy_action,
        name='add_holding_buy_action'),
    path('holding/sell/action/<int:holding_buy_order_id>/add/',
        position.open_positions.add_holding_sell_action,
        name='add_holding_sell_action'),

    path('holding/buy/action/<int:holding_buy_action_id>/',
         position.open_positions.get_holding_buy_action,
         name='get_holding_buy_action'),
    path('holding/buy/action/<int:holding_buy_action_id>/edit/',
         position.open_positions.edit_holding_buy_action,
         name='edit_holding_buy_action'),
    path('holding/buy/action/<int:holding_buy_action_id>/delete/',
         position.open_positions.delete_holding_buy_action,
         name='delete_holding_buy_action'),

    path('holding/sell/action/<int:holding_sell_action_id>/',
         position.open_positions.get_holding_sell_action,
         name='get_holding_sell_action'),
    path('holding/sell/action/<int:holding_sell_action_id>/edit/',
         position.open_positions.edit_holding_sell_action,
         name='edit_holding_sell_action'),
    path('holding/sell/action/<int:holding_sell_action_id>/delete/',
         position.open_positions.delete_holding_sell_action,
         name='delete_holding_sell_action'),


    ####### Obsolete  #######
    # Open Positions -> Transaction -> Delete
    path('delete/<str:transaction_id>/',
        position.open_positions.delete_transaction,
        name='delete_transaction'),

    ####### position.adjust_stop_limits #######
    # Adjust Stop Limit  -> Default
    path('adjust_stop_limits/',
        position.adjust_stop_limits.default,
        name='adjust_stop_limits'),

    ####### position.close_position #######
    # Close Position  -> Default
    path('close_positions/',
        position.close_positions.default,
        name='close_positions'),


    # Obsolete
    # Open Positions -> Transactions -> List
    path('<int:portfolio_id>/item/<int:portfolio_item_id>/transactions/',
        position.open_positions.get_transaction_history,
        name='transactions'),
    # Open Positions -> Transaction -> Add
    path('add/transaction/',
        position.open_positions.add_transaction,
        name='add_transaction'),
]