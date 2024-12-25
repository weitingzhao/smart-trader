from django.urls import path
from home.views import analytics

#all below path with [analytics]
urlpatterns = [

    ####### analytics.risk_analysis #######
    # Wishlist Overview -> Default
    path('risk_analysis/<str:symbol>/<str:cut_over>/',analytics.risk_analysis.default, name='risk_analysis'),

    ####### analytics.performance_analytics #######
    # Saved Screeners -> Default
    path('performance_analytics/', analytics.performance_analytics.default, name='performance_analytics'),

    ####### analytics.market_comparison #######
    # Screening Result -> Default
    path('market_comparison/', analytics.market_comparison.default, name='market_comparison'),
]