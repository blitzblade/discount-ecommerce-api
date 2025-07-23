from rest_framework import serializers
from .models import Order, OrderItem, OrderReview, Coupon, CouponUsage
from api.products.serializers import ProductReadSerializer
from api.users.serializers import AddressSerializer

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value', 'usage_limit', 'usage_limit_per_user',
            'valid_from', 'valid_to', 'active', 'min_order_amount', 'max_discount', 'created_at', 'updated_at'
        ]
        read_only_fields = fields

class CouponUsageSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = CouponUsage
        fields = ['id', 'coupon', 'user', 'user_email', 'order', 'used_at']
        read_only_fields = fields

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'created_at', 'updated_at']
        read_only_fields = fields

class OrderReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = OrderReview
        fields = ['id', 'order', 'user', 'user_email', 'rating', 'review', 'created_at', 'updated_at']
        read_only_fields = ['id', 'order', 'user_email', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    reviews = OrderReviewSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'address', 'status', 'total', 'discount', 'tax', 'shipping',
            'coupon', 'checked_out_at', 'items', 'reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = fields 