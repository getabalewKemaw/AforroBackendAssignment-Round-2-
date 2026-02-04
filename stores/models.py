from django.db import models

from products.models import Product


class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_items')
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'product'], name='unique_store_product_inventory'),
        ]
        indexes = [
            models.Index(fields=['store', 'product']),
        ]

    def __str__(self) -> str:
        return f'{self.store} - {self.product}'

# Create your models here.
