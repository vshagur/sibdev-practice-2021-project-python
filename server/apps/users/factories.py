import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('email',)

    username = factory.faker.Faker('user_name')
    email = factory.LazyAttribute(lambda o: '%s@example.com' % o.username)
    password = factory.faker.Faker('password')
