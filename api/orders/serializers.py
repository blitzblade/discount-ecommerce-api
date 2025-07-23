from rest_framework import serializers
from .models import Order, OrderItem, OrderReview
from api.products.serializers import ProductReadSerializer
from api.users.serializers import AddressSerializer

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

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'address', 'status', 'total', 'discount', 'tax', 'shipping',
            'coupon_code', 'checked_out_at', 'items', 'reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = fields 