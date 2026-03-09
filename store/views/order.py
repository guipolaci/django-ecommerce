from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from store.selectors.cart import get_cart_by_session
from store.services.order import checkout, list_user_orders, retrieve_order


@login_required
def checkout_view(request):
    """
    GET  → shows the cart summary before confirming the order
    POST → places the order, clears the cart, redirects to confirmation

    The view is thin — all business logic lives in the checkout service.
    """

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.method == "POST":
        result = checkout(session_key, request.user)

        if result["success"]:
            return redirect("order_confirmation", order_id=result["order"].id)

        return render(request, "store/order/checkout.html", {
            "cart": get_cart_by_session(session_key),
            "error": result["error"],
        })

    cart = get_cart_by_session(session_key)

    return render(request, "store/order/checkout.html", {"cart": cart})


@login_required
def order_confirmation(request, order_id: int):
    """
    Shows the order confirmation page after a successful checkout.
    If the order doesn't exist or doesn't belong to the user, redirects to orders list.
    """

    order = retrieve_order(order_id, request.user)

    if order is None:
        return redirect("order_list")

    return render(request, "store/order/confirmation.html", {"order": order})


@login_required
def order_list(request):
    """
    Shows all orders placed by the logged-in user.
    """

    orders = list_user_orders(request.user)

    return render(request, "store/order/list.html", {"orders": orders})


@login_required
def order_detail(request, order_id: int):
    """
    Shows the detail of a single order.
    If the order doesn't exist or belongs to another user, redirects to orders list.
    """

    order = retrieve_order(order_id, request.user)

    if order is None:
        return redirect("order_list")

    return render(request, "store/order/detail.html", {"order": order})