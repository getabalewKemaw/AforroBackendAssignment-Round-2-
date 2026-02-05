from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.stores.models import Store


#This serializer is used only for validating incoming request data, not for persistence.
class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity_requested = serializers.IntegerField(min_value=1)
class OrderCreateSerializer(serializers.Serializer):
    store_id = serializers.IntegerField(min_value=1)
    items = OrderItemInputSerializer(many=True)
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        return value
    def validate(self, attrs):
        try:
            store = Store.objects.get(pk=attrs['store_id'])
        except Store.DoesNotExist:
            raise serializers.ValidationError({'store_id': 'Store not found.'})
        product_quantities = {}
        # merge the duplicate products
        """       [
        {"product_id": 1, "quantity_requested": 2},
        {"product_id": 1, "quantity_requested": 3}
                ] """
        #  normalize the input data to enforce uniqueness at the application layer
        for item in attrs['items']:
            product_quantities[item['product_id']] = (
                product_quantities.get(item['product_id'], 0) + item['quantity_requested']
            )

        product_ids = list(product_quantities.keys())
        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise serializers.ValidationError({'items': 'One or more products are invalid.'})
        #convert query results into a lookup map for efficient access.
        product_map = {product.id: product for product in products}
        #prepares clean, validated, DB-ready data.
        items = [
            {
                'product': product_map[product_id],
                'quantity_requested': quantity,
            }
            for product_id, quantity in product_quantities.items()
        ]
        return {
            'store': store,
            'items': items,
        }


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    product_title = serializers.CharField(source='product.title')

    class Meta:
        model = OrderItem
        fields = ('product_id', 'product_title', 'quantity_requested')


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'store_id', 'status', 'created_at', 'items')


class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'created_at', 'total_items')
