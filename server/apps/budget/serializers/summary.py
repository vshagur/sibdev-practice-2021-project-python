from rest_framework.serializers import CharField, IntegerField, Serializer


class SummaryListSerializer(Serializer):
    category_type = CharField(source='category__category_type')
    id = IntegerField(source='category__id')
    name = CharField(source='category__name')
    total_by_expenses = CharField()

    class Meta:
        fields = (
            'category_type', 'id', 'name', 'total_by_expenses'
        )
