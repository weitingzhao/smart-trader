from rest_framework import serializers
from apps.common.models import *



class MarketSymbolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MarketSymbol
        fields = ['url', 'symbol', 'name','market','asset_type']
        extra_kwargs = {
            'url' : {'view_name': 'market-symbol-detail', 'lookup_field': 'symbol'}  # Update 'symbol' to the actual primary key field
        }

