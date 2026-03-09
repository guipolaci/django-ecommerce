from django.db import models
from django.contrib.auth.models import User

from store.models.product import Product


class Order(models.Model):
    """
    Represents a placed order by an authenticated user.

    An order is a snapshot of a cart at the moment of checkout.
    Once created, it should not be affected by product price changes.
    """

    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pendente'
        CONFIRMED = 'confirmed', 'Confirmado'
        CANCELLED = 'cancelled', 'Cancelado'

    # The user who placed the order
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # Order status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # When the order was placed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order #{self.id} — {self.user.username} — {self.status}"

    def get_total(self):
        """
        Calculates the order total based on the price locked at purchase time.
        Uses item.price (not item.product.price) to preserve historical accuracy.
        """
        return sum(item.get_total_price() for item in self.items.all())


class OrderItem(models.Model):
    """
    Represents a single product line inside an order.

    The price is copied from the product at checkout time and stored here.
    This ensures the order total never changes even if the product price changes later.
    """

    # Reference to the parent order
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Reference to the product (kept for display purposes)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    # Quantity ordered
    quantity = models.PositiveIntegerField()

    # Price locked at the moment of checkout — never changes after this
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity} @ R${self.price}"

    def get_total_price(self):
        """
        Returns the line total using the locked price.
        """
        return self.quantity * self.price