from rest_framework import serializers

from apps.products.models import Product


class ProductSearchSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    inventory_quantity = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'description',
            'price',
            'category_name',
            'created_at',
            'inventory_quantity',
        )
