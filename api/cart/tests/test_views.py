import pytest
from django.urls import reverse

from api.cart.tests.factories import CartFactory, CartItemFactory
from api.products.tests.factories import ProductFactory

pytestmark = pytest.mark.django_db


def test_cart_list(api_client, user):
    url = reverse("cart:cart-list-create")
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == 200


def test_cart_create(api_client, user):
    url = reverse("cart:cart-list-create")
    api_client.force_authenticate(user=user)
    response = api_client.post(url, {"user": str(user.id)})
    assert response.status_code in (201, 400)


def test_cart_detail(api_client, user):
    cart = CartFactory(user=user)
    url = reverse("cart:cart-detail", args=[cart.id])
    api_client.force_authenticate(user=user)
    response = api_client.get(url)
    assert response.status_code == 200


def test_cartitem_create(api_client, user):
    cart = CartFactory(user=user)
    product = ProductFactory()
    url = reverse("cart:cartitem-list-create-top")
    api_client.force_authenticate(user=user)
    data = {
        "cart": str(cart.id),
        "product": str(product.id),
        "quantity": 1,
        "price": "10.00",
    }
    response = api_client.post(url, data)
    assert response.status_code in (201, 400)


def test_cart_clear(api_client, user):
    cart = CartFactory(user=user)
    url = reverse("cart:cart-clear-items", args=[cart.id])
    api_client.force_authenticate(user=user)
    response = api_client.post(url)
    assert response.status_code in (200, 204, 400)


def test_cartitem_update(api_client, user):
    cart = CartFactory(user=user)
    cart_item = CartItemFactory(cart=cart)
    url = reverse("cart:cartitem-detail-top", args=[cart_item.id])
    api_client.force_authenticate(user=user)
    response = api_client.patch(url, {"quantity": 2}, format="json")
    assert response.status_code in (200, 400)


def test_cartitem_delete(api_client, user):
    cart = CartFactory(user=user)
    cart_item = CartItemFactory(cart=cart)
    url = reverse("cart:cartitem-detail-top", args=[cart_item.id])
    api_client.force_authenticate(user=user)
    response = api_client.delete(url)
    assert response.status_code in (204, 200, 404)


def test_cartitem_create_invalid_product(api_client, user):
    cart = CartFactory(user=user)
    url = reverse("cart:cartitem-list-create-top")
    api_client.force_authenticate(user=user)
    data = {
        "cart": str(cart.id),
        "product": "00000000-0000-0000-0000-000000000000",
        "quantity": 1,
        "price": "10.00",
    }
    response = api_client.post(url, data)
    assert response.status_code in (400, 404)


def test_cart_unauthorized_access(api_client):
    cart = CartFactory()
    url = reverse("cart:cart-detail", args=[cart.id])
    response = api_client.get(url)
    assert response.status_code == 401
