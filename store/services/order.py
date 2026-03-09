from django.contrib.auth.models import User

from store.models.order import Order, OrderItem
from store.selectors.cart import get_cart_by_session
from store.selectors.order import get_orders_by_user, get_order_by_id


def checkout(session_key: str, user: User):
    """
    Business rule for placing an order.

    Steps:
    1. Fetch the user's current cart
    2. Validate the cart is not empty
    3. Create the Order
    4. For each cart item, create an OrderItem with the price locked at this moment
    5. Clear the cart

    Returns a dict with:
    - success: bool
    - order: Order instance (only when success is True)
    - error: str (only when success is False)
    """

    cart = get_cart_by_session(session_key)

    if cart.is_empty():
        return {"success": False, "error": "Seu carrinho está vazio."}

    # Create the order
    order = Order.objects.create(user=user)

    # Lock each item's price at this exact moment
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,   # price snapshot — never changes after this
        )

    # Clear the cart after order is placed
    cart.items.all().delete()

    return {"success": True, "order": order}


def list_user_orders(user: User):
    """
    Returns all orders placed by the user.
    Delegates to selector — no business rules here.
    """
    return get_orders_by_user(user)


def retrieve_order(order_id: int, user: User):
    """
    Returns a single order detail for the given user.
    Delegates to selector — no business rules here.
    """
    return get_order_by_id(order_id, user)