from django.apps import AppConfig


class CategoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api.category"
    verbose_name = "Category"
