from .models.budget.category import Category
from .models.budget.transaction import Transaction
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request: Request, view: View,
                              obj: [Category, Transaction]) -> bool:
        return obj.owner == request.user
