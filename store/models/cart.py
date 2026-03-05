from django.db import models
from store.models import Product

class Cart(models.Model):
    """
    Represents a shopping cart linked to a session.
    Responsible only for cart identity and creation timestamp.
    """

    # Unique session identifier
    session_key = models.CharField(max_length=40, unique=True)

    # Creation date of the cart
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        String representation of the cart.
        """
        return f"Cart {self.session_key}"

    def is_empty(self) -> bool:
        """
        Check if cart has no items.
        """
        return not self.items.exists()

    def get_total(self):
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    """
    Represents a product inside a cart.
    Responsible for quantity and product relation.
    """

    # Reference to the cart
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    # Reference to the product
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    # Quantity of the product
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        """
        String representation of the cart item.
        """
        return f"{self.product.name} - {self.quantity}"

    def increase_quantity(self, amount: int = 1) -> None:
        """
        Increase item quantity.
        Encapsulates quantity modification behavior.
        """
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount: int = 1) -> None:
        """
            Decrease item quantity.
            If quantity reaches 0, delete the item.
            """

        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()

    def set_quantity(self, amount: int) -> None:
        """
        Set item quantity.
        If quantity <= 0, remove item.
        """

        if amount > 0:
            self.quantity = amount
            self.save()
        else:
            self.delete()

    def get_total_price(self):
        return self.quantity * self.product.price