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


class CartItemReadSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer(read_only=True)

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
        read_only_fields = [
            "id",
            "cart",
            "product",
            "price",
            "created_at",
            "updated_at",
        ]


class CartSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "is_active",
            "checked_out",
            "items_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "is_active",
            "checked_out",
            "items_count",
            "created_at",
            "updated_at",
        ]

    def get_items_count(self, obj):
        return obj.items.count()
