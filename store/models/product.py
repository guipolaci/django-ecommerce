from django.db import models


class Product(models.Model):
    """
    Represents a product entity in the system.
    Responsible only for data structure and simple domain behavior.
    """

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # Stock quantity — how many units are available for purchase
    stock = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.name

    def is_available(self) -> bool:
        """
        Returns True if the product has at least 1 unit in stock.
        Used by views and templates to decide whether to show the add-to-cart button.
        """
        return self.stock > 0

    def has_enough_stock(self, quantity: int) -> bool:
        """
        Returns True if there is enough stock to fulfill the requested quantity.
        Used before adding to cart or checking out.
        """
        return self.stock >= quantity

    def decrease_stock(self, quantity: int) -> None:
        """
        Decreases stock by the given quantity.
        Should only be called after has_enough_stock() confirms availability.
        Like physically removing items from a warehouse shelf.
        """
        self.stock -= quantity
        self.save()