import factory
import factory.fuzzy
from api.users.models import User, Profile, Address

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    phonenumber = factory.Sequence(lambda n: f'+233200000{n:03d}')
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_email_verified = True
    is_phonenumber_verified = True
    role = 'customer'

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
    user = factory.SubFactory(UserFactory)
    bio = factory.Faker('sentence')
    website = factory.Faker('url')

class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address
    user = factory.SubFactory(UserFactory)
    line1 = factory.Faker('street_address')
    line2 = factory.Faker('secondary_address')
    city = factory.Faker('city')
    state = factory.Faker('state')
    postal_code = factory.Faker('postcode')
    country = factory.Faker('country')
    is_default = False 