import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

# Orders
from api.orders.tests.factories import CouponFactory, CouponUsageFactory, OrderFactory, OrderItemFactory, OrderReviewFactory
# Users
from api.users.tests.factories import UserFactory, ProfileFactory, AddressFactory
# Products
from api.products.tests.factories import ProductFactory, ProductImageFactory, ProductVariantFactory, ProductReviewFactory
# Category
from api.category.tests.factories import CategoryFactory, TagFactory
# Cart
from api.cart.tests.factories import CartFactory, CartItemFactory
# Common (abstract, for inheritance)
from api.common.tests.factories import BaseModelFactory

register(CouponFactory)
register(CouponUsageFactory)
register(OrderFactory)
register(OrderItemFactory)
register(OrderReviewFactory)
register(UserFactory)
register(ProfileFactory)
register(AddressFactory)
register(ProductFactory)
register(ProductImageFactory)
register(ProductVariantFactory)
register(ProductReviewFactory)
register(CategoryFactory)
register(TagFactory)
register(CartFactory)
register(CartItemFactory)
# BaseModelFactory is abstract, not registered as a fixture

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def address(user):
    return AddressFactory(user=user, is_default=True)

@pytest.fixture
def product():
    return ProductFactory()

@pytest.fixture
def coupon():
    return CouponFactory()

@pytest.fixture
def cart(user):
    cart = CartFactory(user=user, is_active=True, checked_out=False)
    return cart

@pytest.fixture
def cart_item(cart, product):
    item = CartItemFactory(cart=cart, product=product)
    # Ensure the cart has at least one item
    cart.items.add(item)
    return item 