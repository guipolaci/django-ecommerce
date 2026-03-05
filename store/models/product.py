from django.db import models


class Product(models.Model):
    """
    Represents a product entity in the system.
    Responsible only for data structure and simple domain behavior.
    """

    # Name of the product
    name = models.CharField(max_length=255)

    # Description of the product
    description = models.TextField()

    # Product price
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        String representation of the product.
        """
        return self.name