from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from api.cart.models import Cart, CartItem
from .models import Order, OrderItem, OrderReview
from .serializers import OrderSerializer, OrderReviewSerializer
from api.common.permissions import IsAdminOrManager

# Create your views here.

class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user, is_active=True)
            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items.exists():
                return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
            address = user.addresses.filter(is_default=True).first() or user.addresses.first()
            if not address:
                return Response({'detail': 'No address found for user.'}, status=status.HTTP_400_BAD_REQUEST)
            coupon_code = request.data.get('coupon_code')
            shipping = 10  # Flat shipping for demo
            tax_rate = 0.05  # 5% tax for demo
            discount = 0
            if coupon_code == 'DISCOUNT10':
                discount = 10
            with transaction.atomic():
                subtotal = 0
                for item in cart_items:
                    subtotal += item.product.price * item.quantity
                tax = round(subtotal * tax_rate, 2)
                total = subtotal + shipping + tax - discount
                order = Order.objects.create(
                    user=user,
                    address=address,
                    status=Order.Status.PENDING,
                    total=total,
                    discount=discount,
                    tax=tax,
                    shipping=shipping,
                    coupon_code=coupon_code or None
                )
                for item in cart_items:
                    price = item.product.price
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        price=price
                    )
                    item.product.stock = max(item.product.stock - item.quantity, 0)
                    item.product.save()
                cart.items.all().delete()
                cart.is_active = False
                cart.checked_out = True
                cart.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({'detail': str(exc), 'type': type(exc).__name__}, status=status.HTTP_400_BAD_REQUEST)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-checked_out_at')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            new_status = request.data.get('status')
            tracking_number = request.data.get('tracking_number')
            admin_note = request.data.get('admin_note')
            if tracking_number is not None:
                order.tracking_number = tracking_number
            if admin_note is not None:
                order.admin_note = admin_note
            if new_status:
                if order.set_status(new_status):
                    return Response({'detail': f'Status updated to {new_status}.'})
                else:
                    return Response({'detail': 'Invalid status transition.'}, status=status.HTTP_400_BAD_REQUEST)
            order.save()
            return Response({'detail': 'Order updated.'})
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({'detail': str(exc), 'type': type(exc).__name__}, status=status.HTTP_400_BAD_REQUEST)

class OrderReviewCreateView(generics.CreateAPIView):
    serializer_class = OrderReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = Order.objects.get(pk=self.request.data['order'])
        if order.user != self.request.user or order.status != Order.Status.DELIVERED:
            raise PermissionError('You can only review your own delivered orders.')
        serializer.save(user=self.request.user, order=order)
