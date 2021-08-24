from apps.budget.querysets import TransactionQuerySet
from django.contrib.auth import get_user_model
from django.db import models

OWNER_CLASS = get_user_model()


class Transaction(models.Model):
    owner = models.ForeignKey(
        to=OWNER_CLASS,
        on_delete=models.CASCADE,
        verbose_name='owner',
    )

    category = models.ForeignKey(
        to='budget.Category',
        on_delete=models.CASCADE,
        verbose_name='category',
    )

    amount = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        verbose_name='amount',
    )

    date = models.DateField(
        verbose_name='date',
    )

    objects = TransactionQuerySet.as_manager()

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return str(self.pk)
