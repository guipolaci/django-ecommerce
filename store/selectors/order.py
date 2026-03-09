from django.contrib.auth.models import User

from store.models.order import Order

def get_orders_by_user(user: User):
    """
    Retrieve all orders placed by a specific user.
    Returns orders from most recent to oldest.

    This layer is responsible only for read operations.
    No business rules should be placed here.
    """
    return Order.objects.filter(user=user).order_by('-created_at')


def get_order_by_id(order_id: int, user: User):
    """
    Retrieve a single order by ID, ensuring it belongs to the given user.
    Returns None if not found or if the order belongs to another user.

    The user check is a security rule — but it belongs here because
    it is part of the query itself, not a business decision.
    """
    try:
        return Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        return None