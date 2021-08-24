from .models.budget.transaction import Transaction
from django_filters import rest_framework as filters


class BudgetFilterSet(filters.FilterSet):
    start_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = ['start_date', 'end_date']
