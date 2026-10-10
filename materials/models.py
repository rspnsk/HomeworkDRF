from django.db import models
from config import settings


class Course(models.Model):
    """Курс"""

    title = models.CharField(max_length=255, verbose_name='Название курса')
    preview_image = models.ImageField(upload_to='course_previews/', blank=True, null=True, verbose_name='Превью изображения')
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Урок"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    # Поле связи. Один урок всегда принадлежит одному курсу.

    title = models.CharField(max_length=255, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание')
    preview_image = models.ImageField(upload_to='lesson_previews/', blank=True, null=True, verbose_name='Превью изображения')
    video_link = models.URLField(verbose_name='Ссылка на видео')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['id']

    def __str__(self):
        return f"{self.course} - {self.title}"


class Subscription(models.Model):
    """Модель подписки пользователя на обновления курса."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        "materials.Course",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Гарантирует уникальность пары ID пользователя и ID курса в базе данных
        unique_together = ("user", "course")

    def __str__(self):
        return f"Подписка {self.user} на курс {self.course}"
