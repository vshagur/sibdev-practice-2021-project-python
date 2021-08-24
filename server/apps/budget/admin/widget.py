from ..models.budget.widget import Widget
from django.contrib import admin


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    pass
