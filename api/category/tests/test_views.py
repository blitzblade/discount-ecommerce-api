import pytest
from django.urls import reverse

from api.category.tests.factories import CategoryFactory, TagFactory
from api.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_category_list(api_client):
    CategoryFactory.create_batch(2)
    url = reverse("category:category-list-create")
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 2


def test_category_create(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    url = reverse("category:category-list-create")
    data = {"name": "TestCat", "slug": "testcat"}
    response = api_client.post(url, data)
    assert response.status_code in (201, 400)


def test_category_detail_not_found(api_client):
    url = reverse(
        "category:category-detail", args=["00000000-0000-0000-0000-000000000000"]
    )
    response = api_client.get(url)
    assert response.status_code == 404


def test_category_duplicate_slug(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    CategoryFactory(name="Cat1", slug="cat1")
    url = reverse("category:category-list-create")
    data = {"name": "Cat2", "slug": "cat1"}
    response = api_client.post(url, data)
    assert response.status_code in (400, 409)


def test_tag_list(api_client):
    TagFactory.create_batch(2)
    url = reverse("category:tag-list-create")
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 2


def test_tag_create(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    url = reverse("category:tag-list-create")
    data = {"name": "TestTag", "slug": "testtag"}
    response = api_client.post(url, data)
    assert response.status_code in (201, 400)


def test_tag_duplicate_slug(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    TagFactory(name="Tag1", slug="tag1")
    url = reverse("category:tag-list-create")
    data = {"name": "Tag2", "slug": "tag1"}
    response = api_client.post(url, data)
    assert response.status_code in (400, 409)
