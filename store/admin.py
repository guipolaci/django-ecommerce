from django.contrib import admin
from django.utils.html import format_html
from store.models import Product, Cart, CartItem, Order, OrderItem


# ── Product ───────────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product.
    Shows thumbnail, stock editable inline, price formatted.
    """
    list_display  = ("id", "image_thumbnail", "name", "formatted_price", "stock", "is_available", "created_at")
    search_fields = ("name",)
    list_filter   = ("created_at",)
    ordering      = ("-created_at",)
    list_editable = ("stock",)
    readonly_fields = ("image_preview", "created_at")

    fieldsets = (
        ("Informações do Produto", {
            "fields": ("name", "description", "price", "stock")
        }),
        ("Imagem", {
            "fields": ("image", "image_preview")
        }),
        ("Datas", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )

    def image_thumbnail(self, obj):
        """
        Mostra um thumbnail pequeno na lista de produtos.
        Se não tiver imagem, mostra um traço.
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="width:48px; height:48px; object-fit:cover; border-radius:6px;">',
                obj.image.url
            )
        return "—"
    image_thumbnail.short_description = "Foto"

    def image_preview(self, obj):
        """
        Mostra um preview maior na tela de edição do produto.
        """
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px; border-radius:8px; margin-top:8px;">',
                obj.image.url
            )
        return "Nenhuma imagem cadastrada."
    image_preview.short_description = "Preview"

    def formatted_price(self, obj):
        return format_html("R$ {}", obj.price)
    formatted_price.short_description = "Preço"


# ── Cart ──────────────────────────────────────────────────────
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ("id", "session_key", "item_count", "created_at")
    readonly_fields = ("session_key", "created_at")
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Itens"


# ── Order ─────────────────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "get_total_price")

    def get_total_price(self, obj):
        return format_html("R$ {}", obj.get_total_price())
    get_total_price.short_description = "Total"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ("id", "user", "status", "status_badge", "formatted_total", "created_at")
    list_filter   = ("status",)
    search_fields = ("user__username",)
    ordering      = ("-created_at",)
    list_editable = ("status",)
    inlines       = [OrderItemInline]

    def status_badge(self, obj):
        colors = {
            "pending":   ("#f59e0b", "#fffbeb", "Pendente"),
            "confirmed": ("#16a34a", "#f0fdf4", "Confirmado"),
            "cancelled": ("#dc2626", "#fef2f2", "Cancelado"),
        }
        color, bg, label = colors.get(obj.status, ("#6b7280", "#f9fafb", obj.status))
        return format_html(
            '<span style="color:{}; background:{}; padding:2px 10px; '
            'border-radius:12px; font-size:12px; font-weight:600;">{}</span>',
            color, bg, label
        )
    status_badge.short_description = "Status Visual"

    def formatted_total(self, obj):
        return format_html("R$ {}", obj.get_total())
    formatted_total.short_description = "Total"