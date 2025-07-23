from django.contrib import admin

from .models import Product, ProductImage, ProductReview, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "price",
        "discount_price",
        "status",
        "is_available",
        "is_featured",
        "stock",
        "source",
        "source_platform",
        "category",
        "display_tags",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "description",
        "source_platform",
        "category__name",
        "tags__name",
        "slug",
    )
    list_filter = (
        "status",
        "is_available",
        "is_featured",
        "source",
        "source_platform",
        "category",
        "tags",
        "created_at",
    )
    inlines = [ProductImageInline, ProductVariantInline, ProductReviewInline]

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = "Tags"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "alt_text", "created_at", "updated_at")
    search_fields = ("product__name", "alt_text")
    list_filter = ("created_at",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "value", "created_at", "updated_at")
    search_fields = ("product__name", "name", "value")
    list_filter = ("created_at",)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "is_approved",
        "created_at",
        "updated_at",
    )
    search_fields = ("product__name", "user__email", "review")
    list_filter = ("is_approved", "created_at")
