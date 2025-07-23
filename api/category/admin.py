from django.contrib import admin

from .models import Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "created_at", "updated_at")
    search_fields = ("name", "slug", "description")
    list_filter = ("parent", "created_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug", "description")
    list_filter = ("created_at",)
