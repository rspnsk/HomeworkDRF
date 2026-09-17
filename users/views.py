from rest_framework import generics
from .models import Payment
from .serializers import PaymentSerializer
from rest_framework.filters import OrderingFilter
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
