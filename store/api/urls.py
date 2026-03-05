from django.urls import path
from store.api.views.product import (
    ProductListAPIView,
    ProductDetailAPIView,

)
from store.api.views.cart import CartDetailAPI, AddToCartAPI

urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="api_products"),
    path("products/<int:product_id>/", ProductDetailAPIView.as_view(), name="api_product_detail"),
    path("cart/", CartDetailAPI.as_view(), name="api_cart_detail"),
    path("cart/add", AddToCartAPI.as_view(), name="api_add_to_cart"),
]