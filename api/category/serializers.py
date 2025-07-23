from rest_framework import serializers

from .models import Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CategoryBulkUploadSerializer(serializers.Serializer):
    categories = CategorySerializer(many=True)


class TagBulkUploadSerializer(serializers.Serializer):
    tags = TagSerializer(many=True)
