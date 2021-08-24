from ..models.budget.widget import Widget
from rest_framework.serializers import ModelSerializer, ValidationError


class WidgetCreateSerializer(ModelSerializer):
    class Meta:
        model = Widget
        fields = (
            'id', 'category', 'limit', 'duration', 'criterion', 'color', 'creation_at'
        )

    def create(self, validated_data):
        request = self.context['request']
        validated_data['owner'] = request.user
        widget = Widget.objects.create(**validated_data)

        return widget

    def validate_duration(self, value):
        if value.days not in (1, 7, 30):
            raise ValidationError(
                'The duration of the widget must be one of the list [1, 7, 30]'
            )

        return value


class WidgetListSerializer(ModelSerializer):
    class Meta:
        model = Widget
        fields = (
            'id', 'limit', 'updated_at', 'category', 'color', 'creation_at',
            'criterion', 'duration', 'end_date', 'total',
        )

    def validate_duration(self, value):
        return value.days
