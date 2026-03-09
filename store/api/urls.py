from django.urls import path
from store.api.views.product import (
    ProductListAPIView,
    ProductDetailAPIView,
)

from store.api.views.cart import (
    CartDetailAPI,
    AddToCartAPI,
    IncreaseCartItemAPI,
    DecreaseCartItemAPI,
    RemoveCartItemAPI,
    UpdateCartItemAPI,
)

urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="api_products"),
    path("products/<int:product_id>/", ProductDetailAPIView.as_view(), name="api_product_detail"),
    path("cart/", CartDetailAPI.as_view(), name="api_cart_detail"),
    path("cart/add", AddToCartAPI.as_view(), name="api_add_to_cart"),
    path("cart/increase/<int:product_id>/", IncreaseCartItemAPI.as_view(), name="api_increase_cart_item"),
    path("cart/decrease/<int:product_id>/", DecreaseCartItemAPI.as_view(), name="api_decrease_cart_item"),
    path("cart/remove/<int:product_id>/", RemoveCartItemAPI.as_view(), name="api_remove_cart_item"),
    path("cart/update/<int:product_id>/", UpdateCartItemAPI.as_view(), name="api_update_cart_item"),
]