import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from apps.products.models import Category, Product
from apps.stores.models import Inventory, Store


class Command(BaseCommand):
    help = 'Seed data for the assignment requirements.'

    def add_arguments(self, parser):
        parser.add_argument('--categories', type=int, default=10)
        parser.add_argument('--products', type=int, default=1000)
        parser.add_argument('--stores', type=int, default=20)
        parser.add_argument('--min-inventory-per-store', type=int, default=300)

    def handle(self, *args, **options):
        categories_count = options['categories']
        products_count = options['products']
        stores_count = options['stores']
        min_inventory = options['min_inventory_per_store']

        if categories_count < 1 or products_count < 1 or stores_count < 1:
            self.stderr.write('Counts must be >= 1.')
            return

        faker = Faker()

        with transaction.atomic():
            categories = []
            for _ in range(categories_count):
                name = faker.unique.word().title()
                category, _ = Category.objects.get_or_create(name=name)
                categories.append(category)

            existing_products = Product.objects.count()
            products_to_create = max(products_count - existing_products, 0)
            new_products = []
            for idx in range(products_to_create):
                new_products.append(
                    Product(
                        title=faker.sentence(nb_words=3).rstrip('.'),
                        description=faker.sentence(nb_words=10),
                        price=Decimal(random.randrange(100, 20000)) / 100,
                        category=random.choice(categories),
                    )
                )
            if new_products:
                Product.objects.bulk_create(new_products)

            products = list(Product.objects.all())

            stores = []
            for _ in range(stores_count):
                store, _ = Store.objects.get_or_create(
                    name=faker.company(),
                    location=faker.city(),
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
                            quantity=random.randint(1, 100),
                        )
                    )

            if inventory_rows:
                Inventory.objects.bulk_create(inventory_rows, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Seed data created.'))
