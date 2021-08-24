from ..models.budget.transaction import Transaction
from rest_framework import serializers
from rest_framework.serializers import Serializer


class GlobalsDetailSerializer(Serializer):
    totals_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    totals_expense = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Transaction
        fields = ('totals_income', 'totals_expense')
