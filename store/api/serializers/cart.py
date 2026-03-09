from rest_framework import serializers
from store.models import Cart, CartItem
from store.api.serializers.product import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem.
    Responsible for converting CartItem objects into JSON.
    """

    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart.
    Returns cart with all items.
    """

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "session_key", "items"]


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer used to add a product to the cart.
    """

    product_id = serializers.IntegerField()

class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer used to update the quantity of a cart item.
    Quantity must be a positive integer or zero (which removes the item).
    """

    quantity = serializers.IntegerField(min_value=0)