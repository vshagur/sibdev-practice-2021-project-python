from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email: str, password: str, username: str,
                    **extra_fields) -> User:
        """
        Create and save a User with the given email, username and password.
        """
        if not email:
            raise ValueError('The Email must be set')

        if not username:
            raise ValueError('The Username must be set')

        email = self.normalize_email(email)

        user = self.model(
            email=email, password=password, username=username, **extra_fields
        )

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email: str, password: str, username: str,
                         **extra_fields) -> User:
        """
        Create and save a SuperUser with the given email, username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, username, **extra_fields)
