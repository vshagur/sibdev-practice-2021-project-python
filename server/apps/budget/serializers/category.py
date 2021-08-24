from collections import OrderedDict
from typing import Dict

from ..models.budget.category import Category
from rest_framework.serializers import ModelSerializer, ValidationError


class CategoryListSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_type')


class CategoryCreateSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_type')

    def create(self, validated_data: Dict) -> Category:
        validated_data['owner'] = self.context['request'].user
        category = Category(**validated_data)
        category.save()

        return category

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        request = self.context['request']
        category_type = attrs.get('category_type')
        name = attrs.get('name')

        queryset = Category.objects.filter(
            owner=request.user,
            name=name.lower(),
            category_type=category_type,
        )
        if queryset.exists():
            raise ValidationError(f'The category already exists.')

        return attrs

    def validate_name(self, value: str) -> str:
        if not value:
            raise ValidationError(
                'The "name" field value must not be an empty string.'
            )

        return value.lower()

    def validate_category_type(self, value: str) -> str:
        if not value:
            raise ValidationError(
                'The "category"_type field value must not be an empty string.'
            )

        return value
