from django.contrib.auth import get_user_model
from django.db import models

OWNER_CLASS = get_user_model()


class Category(models.Model):
    INCOME = 'IN'
    EXPENSE = 'EX'
    CATEGORY_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    name = models.CharField(
        max_length=150,
        verbose_name='name',
    )

    owner = models.ForeignKey(
        to=OWNER_CLASS,
        on_delete=models.CASCADE,
        verbose_name='owner',
    )

    category_type = models.CharField(
        max_length=150,
        choices=CATEGORY_TYPE_CHOICES,
        verbose_name='category_type',
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = ('name', 'owner', 'category_type',)

    def __str__(self):
        return str(self.pk)
