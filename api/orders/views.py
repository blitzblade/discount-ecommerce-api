from decimal import Decimal

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.cart.models import Cart, CartItem
from api.common.permissions import IsAdminOrManager
from api.common.utils import calculate_shipping, calculate_tax

from .models import Order, OrderItem
from .serializers import (
    CheckoutRequestSerializer,
    CheckoutResponseSerializer,
    OrderReviewSerializer,
    OrderSerializer,
)

# Create your views here.


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Checkout",
        operation_description="Create an order from the user's active cart. Applies optional coupon, calculates shipping and tax, reduces stock, and clears the cart.",
        request_body=CheckoutRequestSerializer,
        responses={
            201: CheckoutResponseSerializer,
            400: openapi.Response("Bad Request: validation or business rule errors."),
        },
    )
    def post(self, request):
        user = request.user
        try:
            address = (
                user.addresses.filter(is_default=True).first() or user.addresses.first()
            )
            if not address:
                return Response(
                    {"detail": "No address found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                cart = Cart.objects.get(user=user, is_active=True)
            except Cart.DoesNotExist:
                return Response(
                    {"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
                )
            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items.exists():
                return Response(
                    {"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
                )
            coupon_code = request.data.get("coupon_code")
            coupon = None
            discount = Decimal("0")
            with transaction.atomic():
                subtotal = Decimal("0")
                for item in cart_items:
                    subtotal += item.product.price * item.quantity
                shipping = calculate_shipping(subtotal, address)
                shipping_warning = None
                if shipping is None:
                    shipping = Decimal("0")
                    shipping_warning = "Delivery is not supported to this country. You may need to arrange pickup."
                tax = calculate_tax(subtotal, address)
                # Coupon logic
                if coupon_code:
                    from .models import Coupon

                    try:
                        coupon = Coupon.objects.get(code=coupon_code)
                        valid, reason = coupon.is_valid_for_user(user, subtotal)
                        if not valid:
                            return Response(
                                {"detail": reason}, status=status.HTTP_400_BAD_REQUEST
                            )
                        discount = coupon.calculate_discount(subtotal)
                    except Coupon.DoesNotExist:
                        return Response(
                            {"detail": "Invalid coupon code."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                total = subtotal + shipping + tax - discount
                order = Order.objects.create(
                    user=user,
                    address=address,
                    status=Order.Status.PENDING,
                    total=total,
                    discount=discount,
                    tax=tax,
                    shipping=shipping,
                    coupon=coupon,
                )
                for item in cart_items:
                    price = item.product.price
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        price=price,
                    )
                    item.product.stock = max(item.product.stock - item.quantity, 0)
                    item.product.save()
                if coupon:
                    from .models import CouponUsage

                    CouponUsage.objects.create(coupon=coupon, user=user, order=order)
                cart.items.all().delete()
                cart.is_active = False
                cart.checked_out = True
                cart.save()
            serializer = OrderSerializer(order)
            data = serializer.data
            if shipping_warning:
                data["shipping_warning"] = shipping_warning
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response(
                {"detail": str(exc), "type": type(exc).__name__},
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "created_at"]
    search_fields = ["tracking_number"]
    ordering_fields = ["created_at", "checked_out_at", "total"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        qs = Order.objects.select_related("user", "address", "coupon").prefetch_related(
            "items"
        )
        if self.request.user.is_staff or getattr(self.request.user, "role", None) in [
            "admin",
            "manager",
        ]:
            qs = qs.all().order_by("-checked_out_at")
            self.search_fields = ["tracking_number", "user__email"]
        else:
            qs = qs.filter(user=self.request.user).order_by("-checked_out_at")
        return qs


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            new_status = request.data.get("status")
            tracking_number = request.data.get("tracking_number")
            admin_note = request.data.get("admin_note")
            if tracking_number is not None:
                order.tracking_number = tracking_number
            if admin_note is not None:
                order.admin_note = admin_note
            if new_status:
                if order.set_status(new_status):
                    return Response({"detail": f"Status updated to {new_status}."})
                else:
                    return Response(
                        {"detail": "Invalid status transition."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            order.save()
            return Response({"detail": "Order updated."})
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc), "type": type(exc).__name__},
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrderReviewCreateView(generics.CreateAPIView):
    serializer_class = OrderReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied

        order = Order.objects.get(pk=self.request.data["order"])
        user = self.request.user
        if order.user != user or order.status != Order.Status.DELIVERED:
            raise PermissionDenied("You can only review your own delivered orders.")
        serializer.save(user=user, order=order)
