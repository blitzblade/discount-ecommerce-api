import csv
from io import StringIO

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.common.permissions import IsAdminOrManager

from .models import Category, Tag
from .serializers import (
    CategoryBulkUploadSerializer,
    CategorySerializer,
    TagBulkUploadSerializer,
    TagSerializer,
)

# Create your views here.


class CategoryListCreateView(generics.ListCreateAPIView):
    """
    List all categories or create a new category.
    - GET: Returns a list of categories with filtering, search, and ordering.
    - POST: Create a new category (admin/manager only).
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["parent"]
    search_fields = ["name", "description", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a category by ID.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryBulkUploadView(APIView):
    """
    Bulk upload categories via JSON (list of categories) or CSV file.
    - JSON: POST a list of category objects or {"categories": [...]}
    - CSV: POST a file with the key 'file' (fields: name, slug, ...)
    Only admin/manager users can access this endpoint.
    Returns a list of created categories and any errors.
    """

    permission_classes = [IsAdminOrManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_description="Bulk upload categories via JSON (list of categories) or CSV file.",
        request_body=CategoryBulkUploadSerializer,
        responses={201: CategorySerializer(many=True)},
    )
    def post(self, request):
        created = []
        errors = []
        try:
            if isinstance(request.data, list):
                for idx, item in enumerate(request.data):
                    serializer = CategorySerializer(data=item)
                    if serializer.is_valid():
                        created.append(serializer.save())
                    else:
                        errors.append({"index": idx, "errors": serializer.errors})
            elif isinstance(request.data, dict) and "categories" in request.data:
                for idx, item in enumerate(request.data["categories"]):
                    serializer = CategorySerializer(data=item)
                    if serializer.is_valid():
                        created.append(serializer.save())
                    else:
                        errors.append({"index": idx, "errors": serializer.errors})
            elif "file" in request.FILES:
                file = request.FILES["file"]
                decoded_file = file.read().decode("utf-8")
                reader = csv.DictReader(StringIO(decoded_file))
                for idx, row in enumerate(reader):
                    serializer = CategorySerializer(data=row)
                    if serializer.is_valid():
                        created.append(serializer.save())
                    else:
                        errors.append({"row": idx + 1, "errors": serializer.errors})
            else:
                return Response(
                    {"detail": "Provide a list of categories (JSON) or a CSV file."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "created": CategorySerializer(created, many=True).data,
                    "errors": errors,
                },
                status=(
                    status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
                ),
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc), "type": type(exc).__name__},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TagListCreateView(generics.ListCreateAPIView):
    """
    List all tags or create a new tag.
    - GET: Returns a list of tags with filtering, search, and ordering.
    - POST: Create a new tag (admin/manager only).
    """

    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ["name", "description", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]


class TagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a tag by ID.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TagBulkUploadView(APIView):
    """
    Bulk upload tags via JSON (list of tags) or CSV file.
    - JSON: POST a list of tag objects or {"tags": [...]}
    - CSV: POST a file with the key 'file' (fields: name, slug, ...)
    Only admin/manager users can access this endpoint.
    Returns a list of created tags and any errors.
    """

    permission_classes = [IsAdminOrManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_description="Bulk upload tags via JSON (list of tags) or CSV file.",
        request_body=TagBulkUploadSerializer,
        responses={201: TagSerializer(many=True)},
    )
    def post(self, request):
        created = []
        errors = []
        try:
            if isinstance(request.data, list):
                for idx, item in enumerate(request.data):
                    serializer = TagSerializer(data=item)
                    if serializer.is_valid():
                        created.append(serializer.save())
                    else:
                        errors.append({"index": idx, "errors": serializer.errors})
            elif isinstance(request.data, dict) and "tags" in request.data:
                for idx, item in enumerate(request.data["tags"]):
                    serializer = TagSerializer(data=item)
                    if serializer.is_valid():
                        created.append(serializer.save())
                    else:
                        errors.append({"index": idx, "errors": serializer.errors})
            elif "file" in request.FILES:
                file = request.FILES["file"]
                decoded_file = file.read().decode("utf-8")
                reader = csv.DictReader(StringIO(decoded_file))
                for idx, row in enumerate(reader):
                    serializer = TagSerializer(data=row)
                    if serializer.is_valid():
                        created.append(serializer.save())
                    else:
                        errors.append({"row": idx + 1, "errors": serializer.errors})
            else:
                return Response(
                    {"detail": "Provide a list of tags (JSON) or a CSV file."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"created": TagSerializer(created, many=True).data, "errors": errors},
                status=(
                    status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
                ),
            )
        except Exception as exc:
            return Response(
                {"detail": str(exc), "type": type(exc).__name__},
                status=status.HTTP_400_BAD_REQUEST,
            )
