from rest_framework import permissions


class IsAdminOrManager(permissions.BasePermission):
    """Allows access only to admin or manager users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            getattr(request.user, "role", None) in ["admin", "manager"]
            or request.user.is_staff
            or request.user.is_superuser
        )
