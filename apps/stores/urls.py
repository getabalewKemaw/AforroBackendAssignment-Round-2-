from django.urls import path

from apps.stores.views import StoreInventoryListView

urlpatterns = [
    path('stores/<int:store_id>/inventory/', StoreInventoryListView.as_view(), name='store-inventory'),
]
