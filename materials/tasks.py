from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """    Фоновая задача для отправки email подписчикам об обновлении курса.    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден."

    # Находим все подписки на этот курс и извлекаем email-адреса пользователей
    subscriptions = Subscription.objects.filter(course=course).select_related('user')
    recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

    if not recipient_list:
        return f"Нет активных подписчиков для курса: {course.title}"

    subject = f"Обновление курса: {course.title}"
    message = f"Здравствуйте!\n\nМатериалы курса '{course.title}', на который вы подписаны, были обновлены. Загляните на платформу, чтобы изучить новые материалы!"

    # Отправка писем
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    return f"Уведомление об обновлении курса '{course.title}' отправлено {len(recipient_list)} пользователям."
