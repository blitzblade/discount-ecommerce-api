from django.urls import path

from .views import (
    CartClearItemsView,
    CartItemListCreateTopView,
    CartItemRetrieveUpdateDestroyTopView,
    CartListCreateView,
    CartRetrieveUpdateView,
)

app_name = "cart"

urlpatterns = [
    # Cart endpoints
    path("", CartListCreateView.as_view(), name="cart-list-create"),
    path("<uuid:pk>/", CartRetrieveUpdateView.as_view(), name="cart-detail"),
    path(
        "<uuid:cart_id>/clear/", CartClearItemsView.as_view(), name="cart-clear-items"
    ),
    # CartItem endpoints (top-level)
    path(
        "cartitems/",
        CartItemListCreateTopView.as_view(),
        name="cartitem-list-create-top",
    ),
    path(
        "cartitems/<uuid:pk>/",
        CartItemRetrieveUpdateDestroyTopView.as_view(),
        name="cartitem-detail-top",
    ),
]
