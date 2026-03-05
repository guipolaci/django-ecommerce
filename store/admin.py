from django.contrib import admin
from store.models import Product, CartItem, Cart


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for Product model.
    """

    # Fields displayed in list page
    list_display = ("id", "name", "price", "created_at")

    # Fields that allow searching
    search_fields = ("name",)

    # Filters available in sidebar
    list_filter = ("created_at",)

    # Default ordering
    ordering = ("-created_at",)

admin.site.register(Cart)
admin.site.register(CartItem)