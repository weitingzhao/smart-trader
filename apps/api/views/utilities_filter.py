from apps.api.serializers import *
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.response import Response


class UtilitiesFilterViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UtilitiesFilterCategorySerializer

    def get_queryset(self):
        return UtilitiesFilter.objects.values('name').annotate(total=Count('id'))

    @action(detail=True, methods=['get'])
    def get_name(self, request, name=None):
        types = (UtilitiesFilter.objects.filter(
            name=name.replace('-','/')
        ).values('key', 'value', 'order').order_by('order'))

        serializer = UtilitiesFilterSerializer(types, many=True)

        return Response(serializer.data)

