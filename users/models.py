from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для создания пользователей без поля username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле Email должно быть заполнено')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Кастомный пользователь с заменой username на email."""

    username = None
    email = models.EmailField(unique=True, blank=False, null=False, verbose_name='email', help_text='Укажите ваш email')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Телефон')
    city = CountryField(blank_label="Выберите город", blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    # ПРИВЯЗЫВАЕМ НАШ КАСТОМНЫЙ МЕНЕДЖЕР
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежей"""

    # Варианты способов оплаты
    CASH = 'cash'
    TRANSFER = 'transfer'

    # для выпадающего списка в админке
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Наличные'),
        (TRANSFER, 'Перевод на счет'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )

    # Поля курса и урока делаем blank=True, null=True, так как оплачивается либо то, либо другое
    paid_course = models.ForeignKey(
        'materials.Course',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный курс'
    )
    paid_lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный урок'
    )

    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=TRANSFER,
        verbose_name='Способ оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']  # Свежие платежи будут сверху

    def __str__(self):
        # Отображаем, за что именно прошел платеж
        item = self.paid_course.title if self.paid_course else self.paid_lesson.title
        return f'Платеж от {self.user.email} за {item} на сумму {self.payment_amount}'
