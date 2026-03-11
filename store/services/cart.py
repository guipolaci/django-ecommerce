from store.models import CartItem
from store.selectors import get_cart_by_session, get_product_by_id


def add_product_to_cart(session_key: str, product_id: int) -> dict:
    """
    Business rule for adding a product to the cart.

    Validates stock availability before adding.
    If item already exists, checks if increasing would exceed stock.

    Returns a dict with:
    - success: bool
    - error: str (only when success is False)
    """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    if not product.is_available():
        return {"success": False, "error": f"'{product.name}' está fora de estoque."}

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        # Item already in cart — check if we can add one more unit
        new_quantity = cart_item.quantity + 1
        if not product.has_enough_stock(new_quantity):
            return {
                "success": False,
                "error": f"Estoque insuficiente. Apenas {product.stock} unidade(s) disponível(is)."
            }
        cart_item.increase_quantity()

    return {"success": True}


def get_cart(session_key: str):
    """
    Returns the cart for a given session.
    """
    return get_cart_by_session(session_key)


def decrease_product_from_cart(session_key: str, product_id: int) -> None:
    """
    Business rule for decreasing a product quantity in the cart.
    If quantity becomes zero, the item is removed.
    No stock validation needed — decreasing never violates stock rules.
    """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.decrease_quantity()
    except CartItem.DoesNotExist:
        pass


def increase_product_from_cart(session_key: str, product_id: int) -> dict:
    """
    Business rule for increasing a product quantity in the cart.
    Validates stock before increasing.

    Returns a dict with:
    - success: bool
    - error: str (only when success is False)
    """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        new_quantity = cart_item.quantity + 1
        if not product.has_enough_stock(new_quantity):
            return {
                "success": False,
                "error": f"Estoque insuficiente. Apenas {product.stock} unidade(s) disponível(is)."
            }
        cart_item.increase_quantity()

    return {"success": True}


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


def update_product_quantity(session_key: str, product_id: int, quantity: int) -> dict:
    """
    Update product quantity in cart.
    Validates that the requested quantity does not exceed available stock.

    Returns a dict with:
    - success: bool
    - error: str (only when success is False)
    """

    cart = get_cart_by_session(session_key)
    product = get_product_by_id(product_id)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)

        if quantity == 0:
            cart_item.delete()
            return {"success": True}

        if not product.has_enough_stock(quantity):
            return {
                "success": False,
                "error": f"Estoque insuficiente. Apenas {product.stock} unidade(s) disponível(is)."
            }

        cart_item.set_quantity(quantity)
        return {"success": True}

    except CartItem.DoesNotExist:
        return {"success": False, "error": "Item não encontrado no carrinho."}