from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from store.selectors.cart import get_cart_by_session
from store.api.serializers.cart import CartSerializer, AddToCartSerializer
from store.services.cart import add_product_to_cart


class CartDetailAPI(APIView):
    """
    API endpoint to retrieve the current cart.
    """

    def get(self, request):

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        cart = get_cart_by_session(session_key)

        serializer = CartSerializer(cart)

        return Response(serializer.data)

class AddToCartAPI(APIView):
    """
    API endpoint to add a product to the cart.
    """

    def post(self, request):

        serializer = AddToCartSerializer(data=request.data)

        if serializer.is_valid():

            product_id = serializer.validated_data["product_id"]

            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key

            # Call business logic
            add_product_to_cart(session_key, product_id)

            return Response(
                {"message": "Product added to cart"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)