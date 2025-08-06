from rest_framework import serializers

from api.products.serializers import ProductReadSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductReadSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=CartItem._meta.get_field("product").related_model.objects.all(),
        source="product",
        write_only=True,
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "product",
            "product_id",
            "quantity",
            "price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "cart", "product", "price", "created_at", "updated_at"]


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
