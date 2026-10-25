from rest_framework import serializers
from .models import Payment, CustomUser
from django_countries.serializers import CountryFieldMixin


class PaymentSerializer(serializers.ModelSerializer):
    """ Сериализатор для перевода платежей в JSON """
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_date', 'paid_course',
            'paid_lesson', 'payment_amount', 'payment_method',
            'session_id', 'payment_url', 'status'
        ]
        # Эти поля клиент не должен передавать вручную, их заполнит сервер
        read_only_fields = ['user', 'payment_amount', 'session_id', 'payment_url', 'status']


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    """ Сериализатор для перевода пользователей в JSON """
    # Пароль пишем только на запись
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'phone_number', 'city', 'avatar')

    def create(self, validated_data):
        """ Переопределяем метод создания пользователя, т.к. стандартный метод
            делает CustomUser(**validated_data), а это сохранит пароль в открытом виде.  """
        # Используем специальный метод менеджера для хэширования пароля
        user = CustomUser.objects.create_user(**validated_data)
        return user
