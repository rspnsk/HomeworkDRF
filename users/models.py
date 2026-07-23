from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField


class CustomUser(AbstractUser):
    """
    Кастомный пользователь с заменой username на email,
    а также дополнительными полями: телефон, город, аватарка.
    """
    # Отключаем стандартное поле username.
    username = None
    # Поле Email становится обязательным и уникальным. Оно будет использоваться вместо стандартного username.
    email = models.EmailField(unique=True, blank=False, null=False, verbose_name='email', help_text='Укажите ваш email')

    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Телефон')
    city = CountryField(blank_label="Выберите город", blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    USERNAME_FIELD = 'email'  # Указываем, что теперь email является полем для входа
    REQUIRED_FIELDS = []  # При создании суперпользователя через команду createsuperuser будут запрошены только обязательные поля.

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
