from rest_framework.test import APITestCase

from apps.orders.models import Order
from apps.products.models import Category, Product
from apps.stores.models import Inventory, Store


class OrderCreationTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Beverages')
        self.product = Product.objects.create(
            title='Coffee',
            description='Ground coffee',
            price='10.00',
            category=self.category,
        )
        self.store = Store.objects.create(name='Main Store', location='Addis')
        Inventory.objects.create(store=self.store, product=self.product, quantity=5)

    def test_order_confirmed_and_stock_deducted(self):
        payload = {
            'store_id': self.store.id,
            'items': [{'product_id': self.product.id, 'quantity_requested': 2}],
        }
        response = self.client.post('/orders/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], Order.Status.CONFIRMED)
        inventory = Inventory.objects.get(store=self.store, product=self.product)
        self.assertEqual(inventory.quantity, 3)

    def test_order_rejected_when_insufficient_stock(self):
        payload = {
            'store_id': self.store.id,
            'items': [{'product_id': self.product.id, 'quantity_requested': 10}],
        }
        response = self.client.post('/orders/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], Order.Status.REJECTED)
        inventory = Inventory.objects.get(store=self.store, product=self.product)
        self.assertEqual(inventory.quantity, 5)
