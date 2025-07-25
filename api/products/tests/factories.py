import factory
import factory.fuzzy

from api.category.models import Category, Tag
from api.products.models import Product, ProductImage, ProductReview, ProductVariant


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda o: o.name.lower())
    description = factory.Faker("sentence")


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda o: o.name.lower())
    description = factory.Faker("sentence")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda o: o.name.lower())
    description = factory.Faker("sentence")
    price = factory.fuzzy.FuzzyDecimal(10, 100)
    category = factory.SubFactory(CategoryFactory)
    status = "active"
    is_available = True
    stock = factory.fuzzy.FuzzyInteger(1, 100)


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    alt_text = factory.Faker("sentence")


class ProductVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductVariant

    product = factory.SubFactory(ProductFactory)
    name = factory.Faker("word")
    value = factory.Faker("word")


class ProductReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductReview

    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory("api.users.tests.factories.UserFactory")
    rating = factory.fuzzy.FuzzyInteger(1, 5)
    review = factory.Faker("sentence")
    is_approved = True
