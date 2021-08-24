from typing import Dict, Type

from ..models.budget.category import Category
from ..models.budget.transaction import Transaction
from ..permissions import IsOwner
from ..serializers import (CategoryCreateSerializer, CategoryListSerializer,
                           SummaryListSerializer)
from apps.budget.viewsets.transaction import TransactionViewSet
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet


class CategoryViewSet(CreateModelMixin,
                      DestroyModelMixin,
                      ListModelMixin,
                      GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    SERIALIZERS_MAP: Dict[str, Type[Serializer]] = {
        'list': CategoryListSerializer,
        'create': CategoryCreateSerializer,
        'summary': SummaryListSerializer,
    }

    def get_serializer_class(self) -> Type[Serializer]:
        return self.SERIALIZERS_MAP[self.action]

    @action(detail=False, methods=['get', ])
    def summary(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())  # filter
        queryset = queryset.get_summary()
        serializer = self.get_serializer(queryset, *args, **kwargs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        if self.action == 'summary':
            queryset = DjangoFilterBackend().filter_queryset(
                self.request, queryset, TransactionViewSet
            )

        return super().filter_queryset(queryset)

    def get_queryset(self) -> QuerySet:
        if self.action == 'list':
            queryset = Category.objects.filter(owner=self.request.user)
        elif self.action == 'summary':
            queryset = Transaction.objects.filter_by_user(self.request.user)
        else:
            queryset = Category.objects.all()

        return queryset
