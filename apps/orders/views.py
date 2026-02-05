from django.db import transaction

from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)
from apps.orders.tasks import send_order_confirmation
from apps.stores.models import Inventory


from apps.products.models import Product
class OrderCreateView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = serializer.validated_data['store']
        items_data = serializer.validated_data['items']
        product_ids = [item['product'].id for item in items_data]#we will make a  lsit of product id the user want to buy.so we can look them all up ay once later.
        #It ensures that if something goes wrong halfway through, the database resets to how it was before (so you don't lose money or stock by accident).
        with transaction.atomic():
            inventory_qs = (
                Inventory.objects.select_for_update()
                .filter(store=store, product_id__in=product_ids)
                .select_related('product')
            )

            inventory_by_product = {inv.product_id: inv for inv in inventory_qs}# it creates a  quick map so we look at them faster(dictionary comprehensions)
            insufficient = False
            for item in items_data:
                inv = inventory_by_product.get(item['product'].id)
                if inv is None or inv.quantity < item['quantity_requested']:
                    insufficient = True
                    break
            order = Order.objects.create(store=store, status=Order.Status.PENDING)
            #bulk create does ->it save all items in one go to make it fast
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
                #then substract the stocks and make the status confirmed .
                for item in items_data:
                    inv = inventory_by_product[item['product'].id]
                    inv.quantity = inv.quantity - item['quantity_requested']
                Inventory.objects.bulk_update(list(inventory_by_product.values()), ['quantity'])
                order.status = Order.Status.CONFIRMED
                order.save(update_fields=['status'])
                send_order_confirmation.delay(order.id)

        order = Order.objects.prefetch_related('items__product').get(pk=order.pk)
        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class StoreOrderListView(APIView):
    def get(self, request, store_id: int):
        orders = (
            Order.objects.filter(store_id=store_id)
            .annotate(total_items=Coalesce(Sum('items__quantity_requested'), 0))
            .order_by('-created_at')
        )
        data = OrderListSerializer(orders, many=True).data
        return Response(data, status=status.HTTP_200_OK)
