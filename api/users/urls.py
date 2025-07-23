from django.urls import path

from .views import (
    AddressListCreateView,
    AddressRetrieveUpdateDestroyView,
    AdminUserDeactivateView,
    AdminUserListView,
    AdminUserUpdateView,
    CurrentUserView,
    CustomTokenObtainPairView,
    EmailVerificationView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PhoneVerificationConfirmView,
    PhoneVerificationRequestView,
    ProfileRetrieveUpdateView,
    UserDeactivateView,
    UserListCreateView,
    UserRegistrationView,
    UserRetrieveUpdateView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="user-login"),
    path("me/", CurrentUserView.as_view(), name="user-me"),
    path("change-password/", PasswordChangeView.as_view(), name="change-password"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("verify-email/", EmailVerificationView.as_view(), name="verify-email"),
    path(
        "verify-phone/request/",
        PhoneVerificationRequestView.as_view(),
        name="verify-phone-request",
    ),
    path(
        "verify-phone/confirm/",
        PhoneVerificationConfirmView.as_view(),
        name="verify-phone-confirm",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("deactivate/", UserDeactivateView.as_view(), name="user-deactivate"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path(
        "admin/users/<uuid:pk>/",
        AdminUserUpdateView.as_view(),
        name="admin-user-update",
    ),
    path(
        "admin/users/<uuid:pk>/deactivate/",
        AdminUserDeactivateView.as_view(),
        name="admin-user-deactivate",
    ),
    path("users/<uuid:pk>/", UserRetrieveUpdateView.as_view(), name="user-detail"),
    path(
        "profiles/<uuid:pk>/",
        ProfileRetrieveUpdateView.as_view(),
        name="profile-detail",
    ),
    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path(
        "addresses/<uuid:pk>/",
        AddressRetrieveUpdateDestroyView.as_view(),
        name="address-detail",
    ),
    path("", UserListCreateView.as_view(), name="user-list-create"),
]
