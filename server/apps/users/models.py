from .managers import CustomUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
    )

    username = models.CharField(
        verbose_name=_('username'),
        max_length=150,
        validators=[AbstractUser.username_validator, ],
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
