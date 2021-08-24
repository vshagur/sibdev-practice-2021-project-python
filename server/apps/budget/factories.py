from datetime import date, timedelta

from ..users.factories import UserFactory
from .models.budget.category import Category
from .models.budget.transaction import Transaction
from .models.budget.widget import Widget
from factory import Faker, Iterator, LazyAttribute, SubFactory, django, fuzzy


class CategoryFactory(django.DjangoModelFactory):
    """
    Factory for Category models
    """

    class Meta:
        model = Category
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText()
    category_type = fuzzy.FuzzyChoice(('IN', 'EX'))
    owner = SubFactory(UserFactory)


class TransactionFactory(django.DjangoModelFactory):
    """
    Factory for Transaction models
    """

    class Meta:
        model = Transaction

    amount = fuzzy.FuzzyDecimal(low=0.02, high=1000.00)
    category = SubFactory(CategoryFactory)
    owner = SubFactory(UserFactory)
    date = fuzzy.FuzzyDate(date(2019, 1, 1))


class WidgetFactory(django.DjangoModelFactory):
    """
    Factory for Widget models
    """

    class Meta:
        model = Widget
        django_get_or_create = ('category',)

    owner = SubFactory(UserFactory)
    category = SubFactory(CategoryFactory, owner=LazyAttribute(lambda o: o.owner))
    creation_at = fuzzy.FuzzyDate(date(2019, 1, 1))
    updated_at = LazyAttribute(lambda o: o.creation_at)
    color = Faker('color')
    criterion = Iterator(['>', '<'])
    duration = fuzzy.FuzzyChoice((timedelta(days=i) for i in (1, 7, 30)))
    limit = fuzzy.FuzzyDecimal(low=0.02, high=1000.00)
