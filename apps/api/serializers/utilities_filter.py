from rest_framework import serializers
from urllib.parse import quote



class UtilitiesFilterCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    total = serializers.IntegerField()
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ['url', 'name', 'total']

    def get_url(self, obj):
        request = self.context.get('request')
        name = quote(obj["name"].replace('/', '-'), safe='')
        return request.build_absolute_uri(f'/api/filter/{name}')


class UtilitiesFilterSerializer(serializers.Serializer):
    name = serializers.CharField()
    key = serializers.CharField()
    value = serializers.CharField()
    order = serializers.IntegerField()