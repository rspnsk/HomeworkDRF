from rest_framework import generics, viewsets, status
from materials import serializers
from .models import Payment, CustomUser
from .serializers import PaymentSerializer, UserSerializer
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .services import create_stripe_product, create_stripe_price, create_stripe_session, retrieve_stripe_session_status

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


class PaymentCreateAPIView(generics.CreateAPIView):
    """Эндпоинт для создания платежа в нашей системе и инициализации сессии в Stripe"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 1. Получаем выбранный курс или урок из валидированных данных
        paid_course = serializer.validated_data.get('paid_course')
        paid_lesson = serializer.validated_data.get('paid_lesson')
        payment_method = serializer.validated_data.get('payment_method')

        # Определяем название и стоимость на основе привязанного объекта
        if paid_course:
            product_name = paid_course.title
            amount = paid_course.price
        elif paid_lesson:
            product_name = paid_lesson.title
            amount = paid_lesson.price
        else:
            raise serializers.ValidationError("Необходимо выбрать либо курс, либо урок для оплаты.")

        # 2. Если выбран способ оплаты через Stripe, запускаем интеграцию
        if payment_method == Payment.STRIPE:
            # Поочередно вызываем цепочку сервисных функций Stripe
            stripe_product_id = create_stripe_product(product_name)
            stripe_price_id = create_stripe_price(stripe_product_id, amount)
            session_id, payment_url = create_stripe_session(stripe_price_id)

            # Сохраняем объект в локальную БД со всеми сгенерированными данными Stripe
            serializer.save(
                user=self.request.user,
                payment_amount=amount,
                session_id=session_id,
                payment_url=payment_url,
                status=Payment.STATUS_CREATED
            )
        else:
            # Логика для обычных платежей (наличные или перевод на счет)
            serializer.save(
                user=self.request.user,
                payment_amount=amount,
                status=Payment.STATUS_PAID  # Предполагаем, что наличные проводятся постфактум администратором
            )


class PaymentStatusRetrieveAPIView(generics.RetrieveAPIView):
    """
    (Опционально) Эндпоинт для ручной проверки статуса платежа.
    Обращается к Stripe по session_id, обновляет статус в БД и возвращает актуальный JSON.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        payment = self.get_object()

        # Если платеж был создан через Stripe и еще не оплачен локально, проверяем его статус в Stripe
        if payment.payment_method == Payment.STRIPE and payment.status != Payment.STATUS_PAID:
            stripe_status = retrieve_stripe_session_status(payment.session_id)

            # Если Stripe подтверждает, что сессия оплачена, обновляем статус в нашей БД
            if stripe_status == "paid":
                payment.status = Payment.STATUS_PAID
                payment.save()
            elif stripe_status == "expired":
                payment.status = Payment.STATUS_CANCELED
                payment.save()

        # Возвращаем стандартный сериализованный ответ с обновленным статусом
        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
