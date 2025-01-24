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
    path('wishlist/fetching/data', screening.wishlist_overview.fetching, name='wishlist_fetching'),
    # wishlist -> Add Portfolio
    path('wishlist_overview/add_wishlist/',screening.wishlist_overview.add_wishlist, name='add_wishlist'),

    # wishlist -> position_sizing
    path('position_sizing/', screening.position_sizing.default, name='position_sizing'),

    # wishlist -> initial_positions
    path('initial_positions/', screening.initial_positions.default, name='initial_positions'),
]