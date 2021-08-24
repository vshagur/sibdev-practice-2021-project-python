from datetime import date
from decimal import Decimal
from typing import Dict

from ..models.budget.category import Category
from ..models.budget.transaction import Transaction
from ..serializers.category import CategoryListSerializer
from rest_framework import serializers


class TransactionListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(many=False)

    class Meta:
        model = Transaction
        fields = ('id', 'category', 'amount', 'date')


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'category', 'amount', 'date')

    def validate_category(self, value: Category) -> Category:
        request = self.context['request']

        if value.owner != request.user:
            raise serializers.ValidationError(
                'The user must be the owner of the category.'
            )

        return value

    def validate_date(self, value: date) -> date:
        if value > date.today():
            raise serializers.ValidationError(
                'The transaction date cannot be later than today.'
            )

        return value

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError(
                'The transaction amount must be greater than 0.'
            )

        return value

    def create(self, validated_data: Dict) -> Transaction:
        validated_data['owner'] = self.context['request'].user
        transaction = Transaction(**validated_data)
        transaction.save()

        return transaction
