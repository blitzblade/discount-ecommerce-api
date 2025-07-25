import pytest
from django.urls import reverse
from api.orders.models import Order, Coupon, CouponUsage
from api.orders.tests.factories import OrderFactory, CouponFactory
from api.users.tests.factories import AddressFactory
from api.cart.tests.factories import CartFactory, CartItemFactory
from api.products.tests.factories import ProductFactory
from django.utils import timezone
import datetime
from rest_framework.test import APIClient
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_checkout_creates_order(api_client, user, address, cart, cart_item):
    # If a coupon is used in the test, ensure it has min_order_amount=0
    if hasattr(cart, 'coupon') and cart.coupon:
        cart.coupon.min_order_amount = 0
        cart.coupon.save()
    api_client.force_authenticate(user=user)
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    assert response.status_code == 201
    assert Order.objects.filter(user=user).exists()


def test_checkout_with_coupon(api_client, user, address, cart, cart_item, coupon):
    coupon.min_order_amount = 0
    coupon.save()
    api_client.force_authenticate(user=user)
    url = reverse('orders:checkout')
    data = {'coupon_code': coupon.code}
    response = api_client.post(url, data)
    if response.status_code != 201:
        print('Checkout with coupon response:', response.status_code, response.data)
    assert response.status_code == 201
    order = Order.objects.get(user=user)
    assert order.coupon == coupon
    assert CouponUsage.objects.filter(user=user, coupon=coupon, order=order).exists()


def test_order_list(api_client, user):
    OrderFactory.create_batch(3, user=user)
    api_client.force_authenticate(user=user)
    url = reverse('orders:order-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 3 


def test_checkout_with_invalid_coupon(api_client, user, address, cart, cart_item):
    api_client.force_authenticate(user=user)
    url = reverse('orders:checkout')
    data = {'coupon_code': 'INVALIDCODE'}
    response = api_client.post(url, data)
    assert response.status_code == 400
    assert 'Invalid coupon code' in str(response.data)

def test_checkout_with_expired_coupon(api_client, user, address, cart, cart_item):
    expired_coupon = CouponFactory(
        valid_from=timezone.now() - datetime.timedelta(days=10),
        valid_to=timezone.now() - datetime.timedelta(days=5),
        active=True
    )
    api_client.force_authenticate(user=user)
    url = reverse('orders:checkout')
    data = {'coupon_code': expired_coupon.code}
    response = api_client.post(url, data)
    assert response.status_code == 400
    assert 'expired' in str(response.data).lower()

def test_checkout_with_coupon_over_usage(api_client, user, address, cart, cart_item):
    coupon = CouponFactory(usage_limit=1, min_order_amount=0)
    # Use the coupon once
    CouponUsage.objects.create(coupon=coupon, user=user, order=OrderFactory(user=user, coupon=coupon))
    api_client.force_authenticate(user=user)
    url = reverse('orders:checkout')
    data = {'coupon_code': coupon.code}
    response = api_client.post(url, data)
    assert response.status_code == 400
    assert 'usage limit' in str(response.data).lower()

def test_checkout_no_address(api_client, user):
    # Remove all addresses for user
    user.addresses.all().delete()
    cart = CartFactory(user=user)
    product = ProductFactory()
    cart_item = CartItemFactory(cart=cart, product=product)
    api_client.force_authenticate(user=user)
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    assert response.status_code == 400
    assert 'No address found' in str(response.data)

def test_checkout_empty_cart(api_client, user, address):
    cart = CartFactory(user=user)
    api_client.force_authenticate(user=user)
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    assert response.status_code == 400
    assert 'Cart is empty' in str(response.data)

def test_order_list_unauthenticated(api_client):
    url = reverse('orders:order-list')
    response = api_client.get(url)
    assert response.status_code == 401 

def test_order_status_transition_valid(api_client, user, address, cart, cart_item):
    api_client.force_authenticate(user=user)
    # Create an order
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    # Promote user to admin/manager for status update
    user.is_staff = True
    user.save()
    api_client.force_authenticate(user=user)
    status_url = reverse('orders:order-status-update', args=[order_id])
    response = api_client.patch(status_url, {'status': 'paid'}, format='json')
    assert response.status_code == 200
    assert 'Status updated to paid' in str(response.data)

def test_order_status_transition_invalid(api_client, user, address, cart, cart_item):
    api_client.force_authenticate(user=user)
    # Create an order
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    # Promote user to admin/manager for status update
    user.is_staff = True
    user.save()
    api_client.force_authenticate(user=user)
    status_url = reverse('orders:order-status-update', args=[order_id])
    # Try to set status directly to delivered (invalid transition)
    response = api_client.patch(status_url, {'status': 'delivered'}, format='json')
    assert response.status_code == 400
    assert 'Invalid status transition' in str(response.data)

def test_order_status_update_permission_denied(api_client, user, address, cart, cart_item):
    api_client.force_authenticate(user=user)
    # Create an order
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    # Try to update status as non-admin
    status_url = reverse('orders:order-status-update', args=[order_id])
    response = api_client.patch(status_url, {'status': 'paid'}, format='json')
    assert response.status_code == 403

def test_order_status_update_not_found(api_client, user):
    user.is_staff = True
    user.save()
    api_client.force_authenticate(user=user)
    status_url = reverse('orders:order-status-update', args=['00000000-0000-0000-0000-000000000000'])
    response = api_client.patch(status_url, {'status': 'paid'}, format='json')
    assert response.status_code == 404
    assert 'Order not found' in str(response.data) 

def test_order_review_creation_success(api_client, user, address, cart, cart_item):
    # Ensure any coupon has min_order_amount=0
    if hasattr(cart, 'coupon') and cart.coupon:
        cart.coupon.min_order_amount = 0
        cart.coupon.save()
    api_client.force_authenticate(user=user)
    # Create and deliver an order
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    order = Order.objects.get(id=order_id)
    order.status = Order.Status.DELIVERED
    order.save()
    order.refresh_from_db()
    review_url = reverse('orders:order-review-create')
    data = {'order': str(order.id), 'rating': 5, 'review': 'Great!'}
    response = api_client.post(review_url, data)
    assert response.status_code == 201
    assert order.reviews.exists()

def test_order_review_creation_not_delivered(api_client, user, address, cart, cart_item):
    api_client.force_authenticate(user=user)
    # Create an order (not delivered)
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    review_url = reverse('orders:order-review-create')
    data = {'order': str(order_id), 'rating': 4, 'review': 'Not delivered yet'}
    response = api_client.post(review_url, data)
    assert response.status_code == 400 or response.status_code == 403

def test_order_review_creation_not_owner(api_client, user, address, cart, cart_item):
    api_client.force_authenticate(user=user)
    # Create and deliver an order for user
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    order = Order.objects.get(id=order_id)
    order.status = Order.Status.DELIVERED
    order.save()
    # Create another user
    from api.users.tests.factories import UserFactory
    other_user = UserFactory()
    api_client.force_authenticate(user=other_user)
    review_url = reverse('orders:order-review-create')
    data = {'order': str(order.id), 'rating': 3, 'review': 'Not my order'}
    response = api_client.post(review_url, data)
    assert response.status_code == 400 or response.status_code == 403 

def test_order_review_duplicate(api_client, user, address, cart, cart_item):
    # Ensure any coupon has min_order_amount=0
    if hasattr(cart, 'coupon') and cart.coupon:
        cart.coupon.min_order_amount = 0
        cart.coupon.save()
    api_client.force_authenticate(user=user)
    # Create and deliver an order
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    order = Order.objects.get(id=order_id)
    order.status = Order.Status.DELIVERED
    order.save()
    order.refresh_from_db()
    review_url = reverse('orders:order-review-create')
    data = {'order': str(order.id), 'rating': 5, 'review': 'First review'}
    if not order.reviews.exists():
        response1 = api_client.post(review_url, data)
        assert response1.status_code == 201
    # Try to review again
    data2 = {'order': str(order.id), 'rating': 4, 'review': 'Second review'}
    response2 = api_client.post(review_url, data2)
    assert response2.status_code in (400, 403)

def test_order_review_invalid_rating(api_client, user, address, cart, cart_item):
    api_client.force_authenticate(user=user)
    # Create and deliver an order
    url = reverse('orders:checkout')
    response = api_client.post(url, {})
    order_id = response.data['id']
    order = Order.objects.get(id=order_id)
    order.status = Order.Status.DELIVERED
    order.save()
    review_url = reverse('orders:order-review-create')
    # Rating too low
    data = {'order': str(order.id), 'rating': 0, 'review': 'Too low'}
    response1 = api_client.post(review_url, data)
    assert response1.status_code in (400, 403)
    # Rating too high
    data2 = {'order': str(order.id), 'rating': 6, 'review': 'Too high'}
    response2 = api_client.post(review_url, data2)
    assert response2.status_code in (400, 403) 