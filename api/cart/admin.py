from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "is_active",
        "checked_out",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__email",)
    list_filter = ("is_active", "checked_out", "created_at")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "price",
        "created_at",
        "updated_at",
    )
    search_fields = ("cart__user__email", "product__name")
    list_filter = ("created_at",)
