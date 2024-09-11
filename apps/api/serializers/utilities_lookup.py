from rest_framework import serializers
from urllib.parse import quote


class UtilitiesLookupCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    total = serializers.IntegerField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'category', 'total']

    def get_url(self, obj):
        request = self.context.get('request')
        category = quote(obj["category"].replace('/', '-'), safe='')
        return request.build_absolute_uri(f'/api/lookup/{category}')


class UtilitiesLookupTypeSerializer(serializers.Serializer):
    category = serializers.CharField()
    type = serializers.CharField()
    total = serializers.IntegerField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'category', 'type', 'total']

    def get_url(self, obj):
        request = self.context.get('request')
        category = quote(obj["category"].replace('/', '-'), safe='')
        type_ = quote(obj["type"].replace('/', '-'), safe='')
        return request.build_absolute_uri(f'/api/lookup/{category}/{type_}')


class UtilitiesLookupSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()