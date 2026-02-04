from django.urls import path

from apps.search.views import ProductSearchView

urlpatterns = [
    path('api/search/products/', ProductSearchView.as_view(), name='product-search'),
]
