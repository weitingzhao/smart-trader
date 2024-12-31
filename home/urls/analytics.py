from django.urls import path
from home.views import analytics

#all below path with [analytics]
urlpatterns = [

    ####### analytics.strategy_analysis #######
    # Wishlist Overview -> Default
    path('strategy_analysis/<str:symbol>/<str:cut_over>/',analytics.strategy_analysis.default, name='strategy_analysis'),

    ####### analytics.strategy_optimize #######
    # Saved Screeners -> Default
    path('strategy_optimize/<str:symbol>/<str:cut_over>/', analytics.strategy_optimize.default, name='strategy_optimize'),

    ####### analytics.market_comparison #######
    # Screening Result -> Default
    path('market_comparison/', analytics.market_comparison.default, name='market_comparison'),
]