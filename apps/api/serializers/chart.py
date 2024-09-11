from rest_framework import serializers
from urllib.parse import quote

from apps.common.models import MarketSymbol


class ChartExchangeSerializer(serializers.Serializer):
    market = serializers.CharField()
    total = serializers.IntegerField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'market', 'total']

    def get_url(self, obj):
        request = self.context.get('request')
        market = quote(obj["market"].replace('/', '-'), safe='')
        return request.build_absolute_uri(f'/api/chart-market/{market}')


class ChartSymbolSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MarketSymbol
        fields = ['symbol', 'name', 'market', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        symbol = obj.symbol
        width = 800  # Default width, replace with actual value if needed
        height = 600  # Default height, replace with actual value if needed
        timeframe = 'daily'  # Default timeframe, replace with actual value if needed
        chart_type = 'candle'  # Default chart type, replace with actual value if needed
        elements = 100
        return request.build_absolute_uri(f'/api/chart/{symbol}/{width}/{height}/{timeframe}/{chart_type}/{elements}')