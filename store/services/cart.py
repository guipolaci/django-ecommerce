from store.models import CartItem
from store.selectors import get_cart_by_session, get_product_by_id


def add_product_to_cart(session_key: str, product_id: int) -> None:
    """
    Business rule for adding a product to the cart.

    If item already exists, increase quantity.
    Otherwise, create a new cart item.
    """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.increase_quantity()

def get_cart(session_key: str):
    """
    Returns the cart for a given session.
    """
    return get_cart_by_session(session_key)

def decrease_product_from_cart(session_key: str, product_id: int) -> None:
    """
       Business rule for decreasing a product quantity in the cart.
       If quantity becomes zero, the item is removed.
       """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.decrease_quantity()
    except CartItem.DoesNotExist:
        pass

def increase_product_from_cart(session_key: str, product_id: int) -> None:

    cart = get_cart(session_key)
    product = get_product_by_id(product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.increase_quantity()

def remove_product_from_cart(session_key: str, product_id: int) -> None:
    """
    Remove product completely from cart.
    """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass

def update_product_quantity(session_key: str, product_id: int, quantity: int) -> None:
    """
        Update product quantity in cart.
        """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.set_quantity(quantity)
    except CartItem.DoesNotExist:
        pass
