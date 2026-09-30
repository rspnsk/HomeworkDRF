from rest_framework import generics, viewsets
from .models import Payment, CustomUser
from .serializers import PaymentSerializer, UserSerializer
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class PaymentListAPIView(generics.ListAPIView):
    """Эндпоинт для вывода списка платежей с фильтрацией и сортировкой."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Подключаем бэкенды для фильтрации и сортировки
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # Настраиваем поля для фильтрования (по курсу, уроку и способу оплаты)
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')

    # Настраиваем поля, по которым можно сортировать список
    ordering_fields = ('payment_date',)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD-операций над пользователями. create (регистрация) доступен всем,
       остальные действия (list, retrieve, update, destroy) — только авторизованным."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Если пользователь регистрируется (action == 'create'), пускаем без авторизации
        if self.action == 'create':         # POST /api/users/ — регистрация
            return [AllowAny()]
        # Для всех остальных действий (просмотр, редактирование, удаление) требуется авторизация
        return [IsAuthenticated()]
