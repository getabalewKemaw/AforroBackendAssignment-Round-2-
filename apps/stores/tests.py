from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

from apps.products.models import Category, Product
from apps.stores.models import Inventory, Store


class InventoryTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Fruit')
        self.store = Store.objects.create(name='Store A', location='Addis')

    def test_inventory_unique_constraint(self):
        product = Product.objects.create(
            title='Apple',
            description='Fresh',
            price='1.00',
            category=self.category,
        )
        Inventory.objects.create(store=self.store, product=product, quantity=3)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Inventory.objects.create(store=self.store, product=product, quantity=2)

    def test_inventory_list_sorted_by_product_title(self):
        product_b = Product.objects.create(
            title='Banana',
            description='Yellow',
            price='1.20',
            category=self.category,
        )
        product_a = Product.objects.create(
            title='Apple',
            description='Red',
            price='1.00',
            category=self.category,
        )
        Inventory.objects.create(store=self.store, product=product_b, quantity=5)
        Inventory.objects.create(store=self.store, product=product_a, quantity=7)

        response = self.client.get(f'/stores/{self.store.id}/inventory/')
        self.assertEqual(response.status_code, 200)
        titles = [item['product_title'] for item in response.data]
        self.assertEqual(titles, ['Apple', 'Banana'])
