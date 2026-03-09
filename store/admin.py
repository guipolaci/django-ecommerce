from django.contrib import admin
from django.utils.html import format_html

from store.models import Product, Cart, CartItem, Order, OrderItem


# ──────────────────────────────────────────────
# Product
# ──────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product.

    Allows searching by name, filtering by creation date,
    and displays price with currency formatting.
    """

    list_display = ("id", "name", "formatted_price", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    def formatted_price(self, obj):
        """
        Displays the price with R$ prefix in the list view.
        format_html is used to safely render HTML in admin columns.
        """
        return format_html("R$ {}", obj.price)

    formatted_price.short_description = "Preço"


# ──────────────────────────────────────────────
# Cart
# ──────────────────────────────────────────────

class CartItemInline(admin.TabularInline):
    """
    Displays CartItems inline inside the Cart admin page.

    Inline means: instead of navigating to a separate CartItem page,
    you see and edit all items directly within the Cart detail screen.
    Like seeing the items of a receipt without opening each one separately.
    """

    model = CartItem
    extra = 0                  # don't show empty extra rows by default
    readonly_fields = ("product", "quantity")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for Cart.
    Shows cart session key, creation date and item count.
    """

    list_display = ("id", "session_key", "item_count", "created_at")
    readonly_fields = ("session_key", "created_at")
    inlines = [CartItemInline]

    def item_count(self, obj):
        """
        Displays how many distinct items are in the cart.
        """
        return obj.items.count()

    item_count.short_description = "Itens"


# ──────────────────────────────────────────────
# Order
# ──────────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    """
    Displays OrderItems inline inside the Order admin page.

    Shows the locked price (price at purchase time) — not the current product price.
    This is intentional: the admin reflects exactly what the customer paid.
    """

    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "get_total_price")

    def get_total_price(self, obj):
        return format_html("R$ {}", obj.get_total_price())

    get_total_price.short_description = "Total"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Order.

    Allows filtering by status (pending, confirmed, cancelled),
    searching by username, and displays the order total.
    Status can be changed directly from the list view.
    """

    list_display = ("id", "user", "status_badge", "formatted_total", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username",)
    ordering = ("-created_at",)
    list_editable = ("status",)  # allows changing status directly in the list
    inlines = [OrderItemInline]

    # Override list_display to allow list_editable alongside status_badge
    # We keep status_badge for visual display and status is the editable field
    list_display = ("id", "user", "status", "status_badge", "formatted_total", "created_at")

    def status_badge(self, obj):
        """
        Renders the status as a colored badge in the list view.
        Green for confirmed, red for cancelled, yellow for pending.
        """
        colors = {
            "pending":   ("#f59e0b", "#fffbeb", "Pendente"),
            "confirmed": ("#16a34a", "#f0fdf4", "Confirmado"),
            "cancelled": ("#dc2626", "#fef2f2", "Cancelado"),
        }
        color, bg, label = colors.get(obj.status, ("#6b7280", "#f9fafb", obj.status))
        return format_html(
            '<span style="color:{}; background:{}; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600;">{}</span>',
            color, bg, label
        )

    status_badge.short_description = "Status Visual"

    def formatted_total(self, obj):
        return format_html("R$ {}", obj.get_total())

    formatted_total.short_description = "Total"