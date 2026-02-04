from django.db.models import Case, F, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.products.models import Product
from apps.search.serializers import ProductSearchSerializer, ProductSuggestSerializer
class ProductSearchView(APIView):
    def get(self, request):
        keyword = request.query_params.get('q', '').strip()
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        store_id = request.query_params.get('store_id')
        in_stock = request.query_params.get('in_stock')
        sort = request.query_params.get('sort', 'relevance')
        products = Product.objects.select_related('category')

        if keyword:
            products = products.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(category__name__icontains=keyword)
            )

        if category:
            if category.isdigit():
                products = products.filter(category_id=int(category))
            else:
                products = products.filter(category__name__icontains=category)

        if min_price:
            try:
                products = products.filter(price__gte=min_price)
            except ValueError:
                return Response({'detail': 'Invalid min_price.'}, status=status.HTTP_400_BAD_REQUEST)

        if max_price:
            try:
                products = products.filter(price__lte=max_price)
            except ValueError:
                return Response({'detail': 'Invalid max_price.'}, status=status.HTTP_400_BAD_REQUEST)

        if store_id:
            products = products.filter(inventory_items__store_id=store_id)
            products = products.annotate(
                inventory_quantity=Coalesce(F('inventory_items__quantity'), Value(0))
            )
            if in_stock in ('1', 'true', 'True'):
                products = products.filter(inventory_items__quantity__gt=0)
        else:
            if in_stock in ('1', 'true', 'True'):
                products = products.filter(inventory_items__quantity__gt=0)

        products = products.distinct()

        if sort == 'price':
            products = products.order_by('price', 'id')
        elif sort == 'newest':
            products = products.order_by('-created_at', 'id')
        else:
            if keyword:
                products = products.annotate(
                    relevance=Coalesce(
                        Sum(
                            Case(
                                When(title__icontains=keyword, then=Value(3)),
                                When(description__icontains=keyword, then=Value(2)),
                                When(category__name__icontains=keyword, then=Value(1)),
                                default=Value(0),
                                output_field=IntegerField(),
                            )
                        ),
                        0,
                    )
                ).order_by('-relevance', '-created_at', 'id')
            else:
                products = products.order_by('-created_at', 'id')

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        page_size = max(1, min(page_size, 100))

        paginator = Paginator(products, page_size)
        page_obj = paginator.get_page(page)
        serializer = ProductSearchSerializer(page_obj.object_list, many=True)

        response = {
            'count': paginator.count,
            'page': page_obj.number,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)


class ProductSuggestView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 3:
            return Response(
                {'detail': 'Query must be at least 3 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prefix_matches = (
            Product.objects.filter(title__istartswith=query)
            .order_by('title')
            .values_list('title', flat=True)[:10]
        )
        remaining = 10 - len(prefix_matches)
        if remaining > 0:
            general_matches = (
                Product.objects.filter(title__icontains=query)
                .exclude(title__istartswith=query)
                .order_by('title')
                .values_list('title', flat=True)[:remaining]
            )
            results = list(prefix_matches) + list(general_matches)
        else:
            results = list(prefix_matches)

        serializer = ProductSuggestSerializer({'results': results})
        return Response(serializer.data, status=status.HTTP_200_OK)

