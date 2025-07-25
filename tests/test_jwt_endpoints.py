import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_jwt_token_obtain_and_protected_access():
    # Create a user
    _ = User.objects.create_user(email="testuser@example.com", password="testpass123")
    client = APIClient()

    # Obtain JWT token
    url = reverse("token_obtain_pair")
    response = client.post(
        url, {"email": "testuser@example.com", "password": "testpass123"}, format="json"
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access" in tokens
    assert "refresh" in tokens

    # Access protected endpoint with token
    client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    protected_url = reverse("test_protected")
    response = client.get(protected_url)
    assert response.status_code == 200
    assert response.json()["message"] == "You are authenticated!"


@pytest.mark.django_db
def test_jwt_token_refresh():
    # Create another user
    _ = User.objects.create_user(
        email="anotheruser@example.com", password="anotherpass123"
    )
    client = APIClient()
    url = reverse("token_obtain_pair")
    response = client.post(
        url,
        {"email": "anotheruser@example.com", "password": "anotherpass123"},
        format="json",
    )
    refresh_token = response.json()["refresh"]
    refresh_url = reverse("token_refresh")
    response = client.post(refresh_url, {"refresh": refresh_token}, format="json")
    assert response.status_code == 200
    assert "access" in response.json()
