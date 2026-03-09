from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from store.services.cart import get_product_by_id, add_product_to_cart, get_cart, decrease_product_from_cart, increase_product_from_cart, remove_product_from_cart, update_product_quantity

@login_required
def add_to_cart(request, product_id: int):
    """
    Handle request to add product to cart.
    View must remain thin.
    """

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    product = get_product_by_id(product_id)

    add_product_to_cart(session_key, product_id)

    messages.success(request, f"{product.name} foi adicionado ao carrinho!")

    return redirect("product_list")

@login_required
def cart_detail(request):
    """
    Responsible only for orchestrating cart visualization.
    No business rules here.
    """

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = get_cart(session_key)

    return render(request, "store/cart/detail.html", {"cart": cart})

@login_required
def decrease_cart_item(request, product_id: int):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    decrease_product_from_cart(session_key, product_id)

    return redirect("cart_detail")

@login_required
def increase_cart_item(request, product_id: int):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    increase_product_from_cart(session_key, product_id)

    return redirect("cart_detail")

@login_required
def remove_cart_item(request, product_id: int):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    remove_product_from_cart(session_key, product_id)

    return redirect("cart_detail")

@login_required
@require_POST
def update_cart_item(request, product_id: int):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    quantity = int(request.POST.get("quantity", 1))

    update_product_quantity(session_key, product_id, quantity)

    return redirect("cart_detail")



