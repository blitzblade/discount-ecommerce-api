from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api.users"
    verbose_name = "Users"

    def ready(self):
        import api.users.signals  # noqa: F401
