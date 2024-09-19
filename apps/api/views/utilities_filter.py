from apps.api.serializers import *
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from itertools import groupby
from operator import itemgetter

class UtilitiesFilterViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UtilitiesFilterCategorySerializer

    def get_queryset(self):
        return UtilitiesFilter.objects.values('name').annotate(total=Count('id'))

    @action(detail=True, methods=['get'])
    def get_filter_by_names(self, request, names=None):
        if names:
            names_list = [name.replace('-', '/') for name in names.split(',')]
        else:
            names_list = []

        types = UtilitiesFilter.objects.filter(
            name__in=names_list
        ).values('name', 'key', 'value', 'order').order_by('name', 'order')

        grouped_data = {}
        for name, group in groupby(types, key=itemgetter('name')):
            grouped_data[name] = list(group)

        return Response(grouped_data)

