from django.contrib.auth.models import User

from store.models.order import Order, OrderItem
from store.selectors.cart import get_cart_by_session
from store.selectors.order import get_orders_by_user, get_order_by_id


def checkout(session_key: str, user: User) -> dict:
    """
    Business rule for placing an order.

    Steps:
    1. Fetch the user's current cart
    2. Validate the cart is not empty
    3. Validate stock availability for every item
    4. Create the Order
    5. For each cart item, create an OrderItem with the price locked at this moment
    6. Decrease stock for each product
    7. Clear the cart

    Returns a dict with:
    - success: bool
    - order: Order instance (only when success is True)
    - error: str (only when success is False)
    """

    cart = get_cart_by_session(session_key)

    if cart.is_empty():
        return {"success": False, "error": "Seu carrinho está vazio."}

    # Validate stock for all items before creating anything.
    # We check everything upfront so we never create a partial order.
    # Like a cashier scanning all items before charging — if one fails, nothing goes through.
    for item in cart.items.all():
        if not item.product.has_enough_stock(item.quantity):
            available = item.product.stock
            return {
                "success": False,
                "error": (
                    f"Estoque insuficiente para '{item.product.name}'. "
                    f"Disponível: {available} unidade(s). "
                    f"Reduza a quantidade no carrinho para continuar."
                )
            }

    # All items passed — now create the order
    order = Order.objects.create(user=user)

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,   # price snapshot — locked at purchase time
        )
        # Decrease stock after the order item is safely recorded
        item.product.decrease_stock(item.quantity)

    # Clear the cart
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