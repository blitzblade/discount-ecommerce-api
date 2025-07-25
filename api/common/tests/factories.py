import factory

from api.common.models import BaseModel


class BaseModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BaseModel
        abstract = True
