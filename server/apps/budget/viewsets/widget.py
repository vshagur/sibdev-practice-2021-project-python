from typing import Dict, Type

from ..models.budget.widget import Widget
from ..permissions import IsOwner
from ..serializers import WidgetCreateSerializer, WidgetListSerializer
from django.db.models.query import QuerySet
from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet


class WidgetViewSet(CreateModelMixin,
                    DestroyModelMixin,
                    ListModelMixin,
                    GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    SERIALIZERS_MAP: Dict[str, Type[ModelSerializer]] = {
        'list': WidgetListSerializer,
        'create': WidgetCreateSerializer,
    }

    def get_serializer_class(self) -> Type[ModelSerializer]:
        return self.SERIALIZERS_MAP[self.action]

    def get_queryset(self) -> QuerySet:
        if self.action == 'list':
            queryset = Widget.objects.filter(owner=self.request.user)
        else:
            queryset = Widget.objects.all()

        return queryset
