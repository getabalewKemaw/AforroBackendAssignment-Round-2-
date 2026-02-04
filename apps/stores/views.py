from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.stores.models import Inventory
from apps.stores.serializers import InventoryListSerializer

class StoreInventoryListView(APIView):
    def get(self, request, store_id: int):
        cache_key = f'store_inventory:{store_id}'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached, status=status.HTTP_200_OK)

        inventory = (
            Inventory.objects.filter(store_id=store_id)
            .select_related('product__category')
            .order_by('product__title')
        )
        data = InventoryListSerializer(inventory, many=True).data
        cache.set(cache_key, data, timeout=60)
        return Response(data, status=status.HTTP_200_OK)
