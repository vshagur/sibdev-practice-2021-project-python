from apps.budget.viewsets import CategoryViewSet, TransactionViewSet, WidgetViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'widgets', WidgetViewSet, basename='widget')

urlpatterns = [
    path('users/', include('apps.users.urls')),
    path('', include(router.urls)),
]
