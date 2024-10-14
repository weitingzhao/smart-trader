from django.urls import path
from home.views import wishlist

#all below path with [wishlist]
urlpatterns = [

    ####### wishlist.wishlist_overview #######
    # Wishlist Overview -> Default
    path(
        'wishlist_overview/',
        wishlist.wishlist_overview.default,
        name='wishlist_overview'),

    ####### wishlist.position_sizing #######
    # Saved Screeners -> Default
    path(
        'position_sizing/',
        wishlist.position_sizing.default,
        name='position_sizing'),

    ####### wishlist.stop_limit_setup #######
    # Screening Result -> Default
    path(
        'stop_limit_setup/',
        wishlist.stop_limit_setup.default,
        name='stop_limit_setup'),
]