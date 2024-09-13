from apps.api.serializers import *
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.response import Response


class UtilitiesLookupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UtilitiesLookupCategorySerializer

    def get_queryset(self):
        return UtilitiesLookup.objects.values('category').annotate(total=Count('id'))

    @action(detail=True, methods=['get'])
    def category(self, request, category=None):
        types = UtilitiesLookup.objects.filter(
            category=category.replace('-','/')
        ).values('type').annotate(total=Count('id'))

        for type_obj in types:
            type_obj['category'] = category
        serializer = UtilitiesLookupTypeSerializer(types, many=True, context={'request': request})

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def type(self, request, category=None, type=None):
        types = (UtilitiesLookup.objects.filter(
            category=category.replace('-','/'), type=type.replace('-','/')
        ).values('key', 'value', 'order').order_by('order'))

        serializer = UtilitiesLookupSerializer(types, many=True)

        return Response(serializer.data)
