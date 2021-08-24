from .models import CustomUser
from .permissions import IsUser
from .serializers import CustomUserCreateSerializer, CustomUserDetailSerializer
from rest_framework import generics, permissions


class UserCreate(generics.CreateAPIView):
    serializer_class = CustomUserCreateSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = CustomUser.objects.all()


class UserDetail(generics.RetrieveAPIView):
    serializer_class = CustomUserDetailSerializer
    permission_classes = (permissions.IsAuthenticated, IsUser)
    queryset = CustomUser.objects.all()
