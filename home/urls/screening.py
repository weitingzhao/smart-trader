from django.urls import path
from home.views import screening

#all below path with [screening]
urlpatterns = [

    ####### quote #######
    path('stock/quote/<str:symbol>', screening.quote.default, name="stock_quote"),

    ####### screener #######
    # screener -> Default
    path('screener/', screening.screener.default, name='screener'),

    #  Screener -> Result
    path('stock/search/', screening.screener.stock_search, name='stock_search'),
    path('rating/output/', screening.screener.output, name='screening_output'),
    path('api/stock_data', screening.screener.get_stock_data, name='get_stock_data'),

    ####### snapshot #######
    # snapshot -> Default
    path('snapshot/', screening.snapshot.default, name='snapshot'),
    path('snapshot/fetching/data', screening.snapshot.fetching, name='snapshot_fetching'),

    ####### wishlist #######
    # wishlist -> Default
    path('wishlist/', screening.wishlist_overview.default, name='wishlist'),
    path('wishlist/get/<str:symbol>/', screening.wishlist_overview.get_wishlist, name='get_wishlist'),

    path('wishlist/add_wishlist/', screening.wishlist_overview.add_wishlist, name='add_wishlist'),
    path('wishlist/update_wishlist/', screening.wishlist_overview.update_wishlist, name='update_wishlist'),
    path('wishlist/fetching/data', screening.wishlist_overview.fetching, name='wishlist_fetching'),
    path('wishlist/<str:symbol>/delete/', screening.wishlist_overview.delete_wishlist, name='delete_wishlist'),
    path('wishlist/update-order/<str:direction>/', screening.wishlist_overview.order_wishlist, name='wishlist_update_order'),

    ####### Monitor #######
    # wishlist -> Default (web socket)
    path('monitor/', screening.monitor.default, name='monitor'),
    path('portfolio/', screening.monitor.portfolio, name='screening_portfolio'),
    path('strategy/<str:strategy_id>/', screening.monitor.strategy, name='screening_strategy'),
    path('quote/<str:symbol>/', screening.monitor.quote, name='screening_quote'),

    # wishlist -> position_sizing
    path('position_sizing/', screening.position_sizing.default, name='position_sizing'),

    # wishlist -> initial_positions
    path('initial_positions/', screening.initial_positions.default, name='initial_positions'),
]