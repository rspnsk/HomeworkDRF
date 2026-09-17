from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Настраиваем колонки, которые будут видны в списке платежей
    list_display = ('id', 'user', 'payment_date', 'paid_course', 'paid_lesson', 'payment_amount', 'payment_method')
    # Добавляем фильтрацию на правую панель
    list_filter = ('payment_method', 'payment_date')
