from typing import Dict

from .models import CustomUser
from django.contrib.auth.models import User
from rest_framework import serializers


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data: Dict) -> User:
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

    def to_representation(self, instance: User) -> Dict:
        return {
            'id': instance.pk,
            'username': instance.username,
        }
