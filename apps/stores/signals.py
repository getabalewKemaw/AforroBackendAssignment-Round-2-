from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.stores.models import Inventory


@receiver([post_save, post_delete], sender=Inventory)
def invalidate_store_inventory_cache(sender, instance: Inventory, **kwargs):
    cache_key = f'store_inventory:{instance.store_id}'
    cache.delete(cache_key)



# cache_key: This creates a specific address for the data. For example, if you update stock for Store #5, the key is "store_inventory:5".
# cache.delete(): This tells the Cache (Redis or Memcached): "Throw away the old data for Store #5."