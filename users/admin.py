from django.contrib import admin
from .models import Payment, CustomUser
from django.contrib.auth.admin import UserAdmin


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Настраиваем колонки, которые будут видны в списке платежей
    list_display = ('id', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'payment_amount', 'payment_method')
    # Добавляем фильтрацию на правую панель
    list_filter = ('payment_method', 'payment_date')



@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения кастомного пользователя в админке."""

    # Отключаем сортировку по username
    ordering = ('email',)

    # Колонки, которые будут видны в таблице списка пользователей
    list_display = ('email', 'phone_number', 'city', 'is_staff', 'is_active')

    # Поля, по которым можно искать пользователей вверху страницы
    search_fields = ('email', 'phone_number')

    # Настройка фильтров на правой панели
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'city',)

    # Структура полей внутри страницы редактирования конкретного пользователя
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('phone_number', 'city', 'avatar')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    # Поля, которые запрашиваются при создании пользователя через админку
    add_fieldsets = (
        (None, {
            'classes': ('collapse',),
            'fields': ('email', 'password', 'is_staff', 'is_active'),
        }),
    )
