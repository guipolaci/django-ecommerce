from django.urls import path
from store.api.views.product import (
    ProductListAPIView,
    ProductDetailAPIView,
)

urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="api_products"),
    path("products/<int:product_id>/", ProductDetailAPIView.as_view(), name="api_product_detail"),
]