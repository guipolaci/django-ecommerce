from store.models import Cart

def get_cart_by_session(session_key: str) -> Cart:
    """
    Retrieve a cart by session key.
    If it does not exist, create one.
    """
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart