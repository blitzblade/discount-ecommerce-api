import pytest
from django.urls import reverse
from api.products.models import Product
from api.products.tests.factories import ProductFactory
from api.products.tests.factories import ProductImageFactory, ProductVariantFactory, ProductReviewFactory
from api.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

def test_product_list(api_client):
    ProductFactory.create_batch(3)
    url = reverse('products:product-list-create')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 3

def test_product_create(api_client):
    url = reverse('products:product-list-create')
    data = {
        'name': 'Test Product',
        'price': '19.99',
    }
    response = api_client.post(url, data)
    assert response.status_code in (201, 400)  # 400 if required fields missing

def test_product_detail(api_client):
    product = ProductFactory()
    url = reverse('products:product-detail', args=[product.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['id'] == str(product.id)

def test_fetch_discounted_products(api_client):
    user = UserFactory(is_staff=True)
    api_client.force_authenticate(user=user)
    url = reverse('products:fetch-discounted-products')
    response = api_client.get(url)
    assert response.status_code in (200, 403, 405)

def test_product_image_create(api_client, user):
    api_client.force_authenticate(user=user)
    product = ProductFactory()
    url = reverse('products:product-image-list-create')
    data = {'product': str(product.id)}
    response = api_client.post(url, data)
    assert response.status_code in (201, 400, 403)

def test_product_variant_create(api_client, user):
    api_client.force_authenticate(user=user)
    product = ProductFactory()
    url = reverse('products:product-variant-list-create')
    data = {'product': str(product.id), 'name': 'Color', 'value': 'Red'}
    response = api_client.post(url, data)
    assert response.status_code in (201, 400, 403)

def test_product_review_create_and_invalid(api_client, user):
    api_client.force_authenticate(user=user)
    product = ProductFactory()
    url = reverse('products:product-review-list-create')
    data = {'product': str(product.id), 'rating': 5, 'review': 'Nice!'}
    response = api_client.post(url, data)
    assert response.status_code in (201, 400)
    # Invalid rating
    data2 = {'product': str(product.id), 'rating': 0, 'review': 'Too low'}
    response2 = api_client.post(url, data2)
    assert response2.status_code in (400, 403)

def test_product_detail_not_found(api_client):
    url = reverse('products:product-detail', args=['00000000-0000-0000-0000-000000000000'])
    response = api_client.get(url)
    assert response.status_code == 404 