from django.urls import path
from home.views import position

#all below path with [position]
urlpatterns = [

    ####### Positions open close #######
    # Open Positions -> Default
    path('open_positions/', position.open_positions.default,  name='open_positions'),
    # Close Position  -> Default
    path('close_positions/', position.close_positions.default,  name='close_positions'),

    ####### holding. trade #######
    path('holding/trade/<int:trade_id>/', position.trade.update_phase,  name='update_trade_phase'),

    ####### order #######
    path('order/create/', position.open_positions.add_order, name='add_order'),

    path('order/<int:order_id>/', position.open_positions.get_order,  name='get_order'),

    path('order/<int:order_id>/edit/', position.open_positions.edit_order, name='edit_order'),

    path('order/<int:order_id>/ref/', position.open_positions.get_order_ref, name='get_order_ref'),

    path('order/<int:order_id>/delete/', position.open_positions.delete_order,  name='delete_order'),

    path('order/<int:order_id>/adjust/', position.open_positions.adjust_order, name='adjust_order'),

    ####### position.adjust_stop_limits #######
    # Adjust Stop Limit  -> Default
    path('adjust_stop_limits/',
        position.adjust_stop_limits.default,
        name='adjust_stop_limits'),

    ####### position.trade #######
    path('trade/<int:trade_id>/calculate/',
         position.open_positions.trade_calculate,
         name='trade_calculate'),
]