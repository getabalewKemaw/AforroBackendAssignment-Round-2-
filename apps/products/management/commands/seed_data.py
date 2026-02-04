import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import Category, Product
from apps.stores.models import Inventory, Store


class Command(BaseCommand):
    help = 'Seed small demo data for local testing.'

    def add_arguments(self, parser):
        parser.add_argument('--categories', type=int, default=5)
        parser.add_argument('--products', type=int, default=50)
        parser.add_argument('--stores', type=int, default=3)
        parser.add_argument('--min-inventory-per-store', type=int, default=10)

    def handle(self, *args, **options):
        categories_count = options['categories']
        products_count = options['products']
        stores_count = options['stores']
        min_inventory = options['min_inventory_per_store']

        if categories_count < 1 or products_count < 1 or stores_count < 1:
            self.stderr.write('Counts must be >= 1.')
            return

        with transaction.atomic():
            categories = []
            for idx in range(categories_count):
                category, _ = Category.objects.get_or_create(name=f'Category {idx + 1}')
                categories.append(category)

            existing_products = Product.objects.count()
            products_to_create = max(products_count - existing_products, 0)
            new_products = []
            for idx in range(products_to_create):
                new_products.append(
                    Product(
                        title=f'Product {existing_products + idx + 1}',
                        description=f'Description for product {existing_products + idx + 1}',
                        price=Decimal(random.randrange(100, 5000)) / 100,
                        category=random.choice(categories),
                    )
                )
            if new_products:
                Product.objects.bulk_create(new_products)

            products = list(Product.objects.all())

            stores = []
            for idx in range(stores_count):
                store, _ = Store.objects.get_or_create(
                    name=f'Store {idx + 1}',
                    location=f'Location {idx + 1}',
                )
                stores.append(store)

            inventory_rows = []
            for store in stores:
                sample_size = min(min_inventory, len(products))
                for product in random.sample(products, sample_size):
                    inventory_rows.append(
                        Inventory(
                            store=store,
                            product=product,
                            quantity=random.randint(1, 50),
                        )
                    )

            if inventory_rows:
                Inventory.objects.bulk_create(inventory_rows, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Seed data created.'))
