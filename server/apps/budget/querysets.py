from decimal import Decimal
from typing import Dict

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Model, Sum
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

OWNER_CLASS = get_user_model()


class TransactionQuerySet(models.QuerySet):
    def filter_by_user(self, user: OWNER_CLASS) -> QuerySet:
        return self.select_related('category').filter(owner=user.pk)

    def get_summary(self) -> QuerySet:
        return self.values('category__id', 'category__name', 'category__category_type', ) \
            .annotate(total_by_expenses=Coalesce(Sum('amount'), Decimal('0.0')))

    def get_totals_income(self) -> Dict[str, Decimal]:
        return self.filter(category__category_type='IN') \
            .aggregate(totals_income=Coalesce(Sum('amount'), Decimal('0.0')))

    def get_totals_expense(self) -> Dict[str, Decimal]:
        return self.filter(category__category_type='EX') \
            .aggregate(totals_expense=Coalesce(Sum('amount'), Decimal('0.00')))

    def get_total_value_by_category(self, category: Model) -> Decimal:
        return self.filter(category=category) \
            .aggregate(totals=Coalesce(Sum('amount'), Decimal('0.00'))) \
            .get('totals')

    def get_totals(self) -> Dict[str, Decimal]:
        return dict(
            **self.get_totals_income(),
            **self.get_totals_expense(),
        )
