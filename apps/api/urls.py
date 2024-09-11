from django.urls import re_path, path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from apps.api.views import *
from apps.api.views.chart import ChartExchangeViewSet, ChartSymbolViewSet

router = routers.DefaultRouter()

router.register(r'market_symbols', MarketSymbolViewSet, basename='market_symbols')
router.register(r'lookup', UtilitiesLookupViewSet, basename='lookup')
router.register(r'chart', ChartExchangeViewSet, basename='chart')

urlpatterns = [
	# authentication
	path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

	# component define
	path('', include(router.urls)),

	# market symbols
	path('market_symbols/<str:symbol>/',
		 MarketSymbolDetailAPIView.as_view(), name='market-symbol-detail'),

	# utilities lookup
	path('lookup/<str:category>',
		 UtilitiesLookupViewSet.as_view({'get': 'category'}), name='lookup-category'),
	path('lookup/<str:category>/<str:type>',
		 UtilitiesLookupViewSet.as_view({'get': 'type'}), name='lookup-type'),

	# Chart
	path('chart-market/<str:market>',
		 ChartSymbolViewSet.as_view({'get': 'list'}), name='chart-market'),
	path('chart/<str:symbol>/<int:width>/<int:height>/<str:timeframe>/<str:chart_type>/<int:elements>',
		 ChartSymbolViewSet.as_view({'get': 'symbol'}), name='chart-symbol'),

]