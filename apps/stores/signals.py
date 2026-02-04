from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.stores.models import Inventory


@receiver([post_save, post_delete], sender=Inventory)
def invalidate_store_inventory_cache(sender, instance: Inventory, **kwargs):
    cache_key = f'store_inventory:{instance.store_id}'
    cache.delete(cache_key)
