from django.urls import path, include
from users.apps import UsersConfig
from users.views import PaymentListAPIView, UserViewSet, PaymentCreateAPIView, PaymentStatusRetrieveAPIView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


app_name = UsersConfig.name

# Роутер для CRUD пользователей
router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),

    # Эндпоинты для интеграции со Stripe (теперь внутри приложения users)
    path("payment/create/", PaymentCreateAPIView.as_view(), name="payment-create"),
    path("payment/status/<int:pk>/", PaymentStatusRetrieveAPIView.as_view(), name="payment-status"),

    path("", include(router.urls)),
]
