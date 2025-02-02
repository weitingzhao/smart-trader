from django.urls import path
from home.views import analytics

#all below path with [analytics]
urlpatterns = [

    ####### analytics.strategy_analysis #######
    # Wishlist Overview -> Default
    path('strategy/',
         analytics.strategy_analysis.default, name='strategy_analysis'),
    path('strategy/test/<str:data>/',
         analytics.strategy_analysis.backtrader_plot, name='strategy_analysis_plot'),

    ####### analytics.strategy_optimize #######
    # Saved Screeners -> Default
    path('strategy_optimize/<str:symbol>/<str:cut_over>/', analytics.strategy_optimize.default, name='strategy_optimize'),

    ####### analytics.market_comparison #######
    # Screening Result -> Default
    path('market_comparison/', analytics.market_comparison.default, name='market_comparison'),
    path('strategy_optimize/save_algo_strategy/',
         analytics.market_comparison.save_algo_strategy, name='save_algo_strategy'),
    path('strategy_optimize/load_algo_strategy/',
         analytics.market_comparison.load_algo_strategy, name='load_algo_strategy'),
]