import factory

from api.cart.models import Cart, CartItem


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory("api.users.tests.factories.UserFactory")
    is_active = True
    checked_out = False


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory("api.products.tests.factories.ProductFactory")
    quantity = 1
    price = factory.LazyAttribute(lambda o: o.product.price)
