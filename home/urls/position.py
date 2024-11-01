from django.urls import path
from home.views import position

#all below path with [position]
urlpatterns = [

    ####### Positions open close #######
    # Open Positions -> Default
    path('open_positions/', position.open_positions.default,  name='open_positions'),
    # Close Position  -> Default
    path('close_positions/', position.close_positions.default,  name='close_positions'),

    ####### holding. buy order #######

    path('holding/buy/order/<int:holding_buy_order_id>/',
        position.open_positions.get_holding_buy_order,
        name='get_holding_buy_order'),

    path('holding/buy/order/create/',
         position.open_positions.add_holding_buy_order,
         name='add_holding_buy_order'),

    path('holding/buy/order/<int:holding_buy_order_id>/edit/',
        position.open_positions.edit_holding_buy_order,
        name='edit_holding_buy_order'),

    path('holding/buy/order/<int:holding_buy_order_id>/delete/',
        position.open_positions.delete_holding_buy_order,
        name='delete_holding_sell_order'),

    ####### holding. sell order #######

    path('holding/sell/order/<int:holding_sell_order_id>/',
         position.open_positions.get_holding_sell_order,
         name='get_holding_sell_order'),

    path('holding/sell/order/create/',
         position.open_positions.add_holding_sell_order,
         name='add_holding_sell_order'),

    path('holding/sell/order/<int:holding_sell_order_id>/edit/',
         position.open_positions.edit_holding_sell_order,
         name='edit_holding_sell_order'),
    path('holding/sell/order/<int:holding_sell_order_id>/delete/',
         position.open_positions.delete_holding_sell_order,
         name='delete_holding_sell_order'),

    ####### position.adjust_stop_limits #######
    # Adjust Stop Limit  -> Default
    path('adjust_stop_limits/',
        position.adjust_stop_limits.default,
        name='adjust_stop_limits'),

]