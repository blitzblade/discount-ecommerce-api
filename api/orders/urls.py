from django.urls import path

from .views import (
    CheckoutView,
    OrderDetailView,
    OrderListView,
    OrderReviewCreateView,
    OrderStatusUpdateView,
)

app_name = "orders"

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("", OrderListView.as_view(), name="order-list"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path(
        "<uuid:pk>/status/", OrderStatusUpdateView.as_view(), name="order-status-update"
    ),
    path("reviews/", OrderReviewCreateView.as_view(), name="order-review-create"),
]
