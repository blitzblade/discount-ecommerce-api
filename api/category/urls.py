from django.urls import path

from .views import (
    CategoryBulkUploadView,
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    TagBulkUploadView,
    TagListCreateView,
    TagRetrieveUpdateDestroyView,
)

app_name = "category"

urlpatterns = [
    path("", CategoryListCreateView.as_view(), name="category-list-create"),
    path(
        "<uuid:pk>/",
        CategoryRetrieveUpdateDestroyView.as_view(),
        name="category-detail",
    ),
    path("bulk-upload/", CategoryBulkUploadView.as_view(), name="category-bulk-upload"),
    path("tags/", TagListCreateView.as_view(), name="tag-list-create"),
    path("tags/<uuid:pk>/", TagRetrieveUpdateDestroyView.as_view(), name="tag-detail"),
    path("tags/bulk-upload/", TagBulkUploadView.as_view(), name="tag-bulk-upload"),
]
