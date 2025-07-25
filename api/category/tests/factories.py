import factory
from api.category.models import Category, Tag

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda o: o.name.lower())
    description = factory.Faker('sentence')
    parent = None

class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda o: o.name.lower())
    description = factory.Faker('sentence') 