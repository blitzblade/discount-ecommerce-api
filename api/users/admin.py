from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile, Address


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["email", "first_name", "last_name", "role", "is_staff", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "is_staff", "is_email_verified", "is_phonenumber_verified", "gender"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username", "first_name", "last_name", "phonenumber", "date_of_birth", "gender", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
        ("Verification", {"fields": ("is_email_verified", "is_phonenumber_verified")}),
        ("Additional Info", {"fields": ("is_deleted", "metadata", "otp_secret")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phonenumber", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name", "phonenumber")
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "bio", "website"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_filter = ["user__role"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "line1", "city", "state", "country", "is_default"]
    list_filter = ["is_default", "country", "state"]
    search_fields = ["user__email", "line1", "city", "state", "country"]
    ordering = ["user__email", "is_default"]


admin.site.register(User, UserAdmin)
