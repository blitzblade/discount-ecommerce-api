from rest_framework import serializers

from api.products.serializers import ProductReadSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "product",
            "quantity",
            "price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "cart", "price", "created_at", "updated_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "is_active",
            "checked_out",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "checked_out",
            "items",
            "created_at",
            "updated_at",
        ]
