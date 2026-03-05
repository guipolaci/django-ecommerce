from rest_framework import serializers
from store.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer responsible for converting Product model
    instances into JSON representation and vice-versa.
    """

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "created_at",
        ]