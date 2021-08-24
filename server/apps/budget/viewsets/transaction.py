from typing import Dict, Type

from ..filters import BudgetFilterSet
from ..models.budget.transaction import Transaction
from ..paginators import TransactionSetPagination
from ..permissions import IsOwner
from ..serializers import (
    GlobalsDetailSerializer, TransactionCreateSerializer, TransactionListSerializer
)
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('date',)
    filterset_class = BudgetFilterSet
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = TransactionSetPagination
    SERIALIZERS_MAP: Dict[str, Type[ModelSerializer]] = {
        'list': TransactionListSerializer,
        'update': TransactionCreateSerializer,
        'partial_update': TransactionCreateSerializer,
        'create': TransactionCreateSerializer,
        'globals': GlobalsDetailSerializer,
    }

    def get_serializer_class(self) -> Type[ModelSerializer]:
        return self.SERIALIZERS_MAP[self.action]

    def get_queryset(self) -> QuerySet:
        if self.action in self.SERIALIZERS_MAP:
            return Transaction.objects.filter_by_user(self.request.user)

        return Transaction.objects.all()

    @action(detail=False, methods=['get', ])
    def globals(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())  # filter here
        queryset = queryset.get_totals()
        serializer = self.get_serializer(queryset, *args, **kwargs, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)
