from datetime import date
from decimal import Decimal

from .transaction import Transaction
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

OWNER_CLASS = get_user_model()


class Widget(models.Model):
    GT = '>'
    LT = '<'
    CRITERION_CHOICES = [
        (GT, 'More than ...'),
        (LT, 'Less than ...'),
    ]

    owner = models.ForeignKey(
        to=OWNER_CLASS,
        on_delete=models.CASCADE,
        verbose_name='owner',
    )

    category = models.ForeignKey(
        to='budget.Category',
        on_delete=models.CASCADE,
        verbose_name='category',
        related_name='widgets',
    )

    limit = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        verbose_name='limit',
    )

    duration = models.DurationField(
        verbose_name='duration',
    )

    criterion = models.CharField(
        max_length=2,
        choices=CRITERION_CHOICES,
        verbose_name='criterion',
    )

    color = ColorField(
        default='#FF0000',  # red, maybe not needed
        verbose_name='color',
    )

    creation_at = models.DateField(
        auto_now_add=True,
        verbose_name='creation_at',
    )

    updated_at = models.DateField(
        auto_now=True,
        verbose_name='updated_at',
    )

    class Meta:
        verbose_name = 'Widget'
        verbose_name_plural = 'Widgets'
        unique_together = ('owner', 'category',)

    def __str__(self):
        return str(self.pk)

    @property
    def end_date(self) -> date:
        return self.creation_at + self.duration

    @property
    def total(self) -> Decimal:
        return Transaction.objects.get_total_value_by_category(category=self.category)
