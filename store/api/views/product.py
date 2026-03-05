from rest_framework.response import Response
from rest_framework.views import APIView
from store.selectors import get_all_products, get_product_by_id
from store.api.serializers.product import ProductSerializer

class ProductListAPIView(APIView):
    """
    API endpoint responsible for listing all products.
    """

    def get(self, request):
        products = get_all_products()

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)


class ProductDetailAPIView(APIView):
    """
    API endpoint responsible for retrieving a single product.
    """

    def get(self, request, product_id: int):
        product = get_product_by_id(product_id)

        serializer = ProductSerializer(product)

        return Response(serializer.data)