from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsUser(permissions.BasePermission):

    def has_object_permission(self, request: Request, view: View, obj: User) -> bool:
        return obj == request.user
