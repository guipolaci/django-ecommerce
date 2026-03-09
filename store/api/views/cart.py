from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from store.selectors.cart import get_cart_by_session
from store.api.serializers.cart import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer
from store.services.cart import add_product_to_cart, increase_product_from_cart, decrease_product_from_cart, remove_product_from_cart, update_product_quantity


def get_or_create_session(request) -> str:
    """
    Helper to ensure the session exists and return its key.
    Avoids repeating this logic in every view.
    """
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


class CartDetailAPI(APIView):
    """
    API endpoint to retrieve the current cart.
    """

    def get(self, request):

        session_key = get_or_create_session(request)

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

            session_key = get_or_create_session(request)

            # Call business logic
            add_product_to_cart(session_key, product_id)

            return Response(
                {"message": "Product added to cart"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IncreaseCartItemAPI(APIView):
    """
    POST /api/cart/increase/<product_id>/
    Increases the quantity of a product in the cart by 1.
    """

    def post(self, request, product_id: int):

        session_key = get_or_create_session(request)

        increase_product_from_cart(session_key, product_id)
        return Response({"message": "Quantity increased"})


class DecreaseCartItemAPI(APIView):
    """
    POST /api/cart/decrease/<product_id>/
    Decreases the quantity of a product by 1.
    If quantity reaches 0, the item is removed from the cart.
    """

    def post(self, request, product_id: int):

        session_key = get_or_create_session(request)

        decrease_product_from_cart(session_key, product_id)
        return Response({"message": "Quantity decreased"})


class RemoveCartItemAPI(APIView):
    """
    DELETE /api/cart/remove/<product_id>/
    Completely removes a product from the cart.
    """

    def delete(self, request, product_id: int):

        session_key = get_or_create_session(request)

        remove_product_from_cart(session_key, product_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateCartItemAPI(APIView):
    """
    PUT /api/cart/update/<product_id>/
    Sets the quantity of a product to a specific value.
    If quantity <= 0, the item is removed.

    Body: { "quantity": <int> }
    """

    def put(self, request, product_id: int):
        serializer = UpdateCartItemSerializer(data=request.data)

        if serializer.is_valid():
            quantity = serializer.validated_data["quantity"]

            session_key = get_or_create_session(request)

            update_product_quantity(session_key, product_id, quantity)
            return Response({"message": "Cart updated"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)