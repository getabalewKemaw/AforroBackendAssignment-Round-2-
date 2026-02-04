from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderCreateSerializer, OrderDetailSerializer
from apps.stores.models import Inventory


class OrderCreateView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = serializer.validated_data['store']
        items_data = serializer.validated_data['items']

        product_ids = [item['product'].id for item in items_data]

        with transaction.atomic():
            inventory_qs = (
                Inventory.objects.select_for_update()
                .filter(store=store, product_id__in=product_ids)
                .select_related('product')
            )
            inventory_by_product = {inv.product_id: inv for inv in inventory_qs}

            insufficient = False
            for item in items_data:
                inv = inventory_by_product.get(item['product'].id)
                if inv is None or inv.quantity < item['quantity_requested']:
                    insufficient = True
                    break

            order = Order.objects.create(store=store, status=Order.Status.PENDING)
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        product=item['product'],
                        quantity_requested=item['quantity_requested'],
                    )
                    for item in items_data
                ]
            )

            if insufficient:
                order.status = Order.Status.REJECTED
                order.save(update_fields=['status'])
            else:
                for item in items_data:
                    inv = inventory_by_product[item['product'].id]
                    inv.quantity = inv.quantity - item['quantity_requested']
                Inventory.objects.bulk_update(list(inventory_by_product.values()), ['quantity'])
                order.status = Order.Status.CONFIRMED
                order.save(update_fields=['status'])

        order = Order.objects.prefetch_related('items__product').get(pk=order.pk)
        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

# Create your views here.
