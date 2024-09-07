from rest_framework import viewsets, generics, permissions
from apps.api.serializers import MarketSymbolSerializer
from apps.common.models import MarketSymbol



class MarketSymbolViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = MarketSymbol.objects.all()
    serializer_class = MarketSymbolSerializer
    lookup_field = 'symbol'  # Update 'symbol' to the actual primary key field

class MarketSymbolDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = MarketSymbol.objects.all()
    serializer_class = MarketSymbolSerializer
    lookup_field = 'symbol'

