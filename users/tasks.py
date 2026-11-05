from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Периодическая задача: проверяет дату последнего входа пользователей.
    Если пользователь не заходил более месяца (30 дней), блокирует его (is_active = False).
    """
    # Вычисляем пороговую дату (текущее время минус 30 дней)
    one_month_ago = timezone.now() - timedelta(days=30)

    # Фильтруем пользователей:
    # 1. Активен (is_active=True)
    # 2. Не является суперпользователем (is_superuser=False), чтобы случайно не заблокировать админа
    # 3. last_login меньше или равен пороговой дате, ЛИБО last_login отсутствует (None) и пользователь создан более 30 дней назад
    inactive_users = User.objects.filter(
        is_active=True,
        is_superuser=False,
        last_login__lte=one_month_ago
    )

    count = inactive_users.count()

    if count > 0:
        # Пакетное обновление флага is_active для повышения производительности
        inactive_users.update(is_active=False)
        return f"Успешно заблокировано неактивных пользователей: {count}."

    return "Неактивных пользователей для блокировки не обнаружено."
