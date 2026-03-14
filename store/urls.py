from django.urls import path
from store.views import product_list, product_detail, add_to_cart
from store.views.cart import cart_detail, decrease_cart_item, increase_cart_item, remove_cart_item, update_cart_item
from store.views.account import register, login_view, logout_view
from store.views.order import checkout_view, order_confirmation, order_list, order_detail
from store.views.dashboard import dashboard_index, dashboard_product_create, dashboard_product_list, dashboard_product_edit, dashboard_product_delete

urlpatterns = [
    # Produtos
    path("", product_list, name="product_list"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),

    # Carrinho
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/decrease/<int:product_id>/", decrease_cart_item, name="decrease_cart_item"),
    path("cart/increase/<int:product_id>/", increase_cart_item, name="increase_cart_item"),
    path("cart/remove/<int:product_id>/", remove_cart_item, name="remove_cart_item"),
    path("cart/update/<int:product_id>/", update_cart_item, name="update_cart_item"),

    # Autenticação
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Pedidos
    path("checkout/", checkout_view, name="checkout"),
    path("orders/", order_list, name="order_list"),
    path("orders/<int:order_id>/", order_detail, name="order_detail"),
    path("orders/<int:order_id>/confirmation/", order_confirmation, name="order_confirmation"),

    # Dashboard
    path("dashboard/", dashboard_index, name="dashboard_index"),
    path("dashboard/products/", dashboard_product_list, name="dashboard_product_list"),
    path("dashboard/products/new/", dashboard_product_create, name="dashboard_product_create"),
    path("dashboard/products/<int:product_id>/edit/", dashboard_product_edit, name="dashboard_product_edit"),
    path("dashboard/products/<int:product_id>/delete/", dashboard_product_delete, name="dashboard_product_delete"),
]