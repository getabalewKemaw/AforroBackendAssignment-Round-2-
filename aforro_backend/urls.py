from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

from rest_framework.response import Response
def root_view(request):
    return JsonResponse(
        {
            'message': 'Afororo Backend Assignment API',
            'endpoints': [
                '/orders/',
                '/stores/<store_id>/orders/',
                '/stores/<store_id>/inventory/',
                '/api/search/products/',
                '/api/search/suggest/',
                '/admin/',
            ],
        }
    )

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('', include('apps.orders.urls')),
    path('', include('apps.stores.urls')),
    path('', include('apps.search.urls')),
]
