import factory
import factory.fuzzy
from api.orders.models import Coupon, CouponUsage, Order, OrderItem, OrderReview
from api.products.models import Product
from api.users.models import User, Address
from django.utils import timezone
import datetime

class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coupon
    code = factory.Faker('bothify', text='COUPON-####')
    discount_type = factory.fuzzy.FuzzyChoice(['fixed', 'percent'])
    discount_value = factory.fuzzy.FuzzyDecimal(5, 50)
    usage_limit = factory.fuzzy.FuzzyInteger(1, 10)
    usage_limit_per_user = factory.fuzzy.FuzzyInteger(1, 5)
    valid_from = factory.LazyFunction(lambda: timezone.now() - datetime.timedelta(days=1))
    valid_to = factory.LazyFunction(lambda: timezone.now() + datetime.timedelta(days=1))
    active = True
    min_order_amount = factory.fuzzy.FuzzyDecimal(0, 100)
    max_discount = factory.fuzzy.FuzzyDecimal(10, 100)

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    user = factory.SubFactory('api.users.tests.factories.UserFactory')
    address = factory.SubFactory('api.users.tests.factories.AddressFactory')
    status = 'pending'
    total = factory.fuzzy.FuzzyDecimal(20, 200)
    discount = factory.fuzzy.FuzzyDecimal(0, 50)
    tax = factory.fuzzy.FuzzyDecimal(0, 20)
    shipping = factory.fuzzy.FuzzyDecimal(5, 20)
    coupon = factory.SubFactory(CouponFactory)

class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory('api.products.tests.factories.ProductFactory')
    product_name = factory.LazyAttribute(lambda o: o.product.name)
    quantity = factory.fuzzy.FuzzyInteger(1, 5)
    price = factory.LazyAttribute(lambda o: o.product.price)

class CouponUsageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CouponUsage
    coupon = factory.SubFactory(CouponFactory)
    user = factory.SubFactory('api.users.tests.factories.UserFactory')
    order = factory.SubFactory(OrderFactory)

class OrderReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderReview
    order = factory.SubFactory(OrderFactory)
    user = factory.SubFactory('api.users.tests.factories.UserFactory')
    rating = factory.fuzzy.FuzzyInteger(1, 5)
    review = factory.Faker('sentence') 