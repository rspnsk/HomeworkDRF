from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import YoutubeUrlValidator


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписки."""

    class Meta:
        model = Subscription
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса."""
    # Объявляем кастомное поле, логика которого описывается в методе get_is_subscribed
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        # Если запроса нет или пользователь анонимный — подписки точно нет
        if not request or not request.user or request.user.is_anonymous:
            return False

        # Проверяем существование подписки текущего пользователя (request.user) на текущий курс (obj)
        return Subscription.objects.filter(user=request.user, course=obj).exists()


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока с валидацией ссылки на видео."""

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YoutubeUrlValidator(field='video_link')]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для курса, выводящий список уроков и их количество."""

    # Вкладываем сериализатор уроков как список.
    # Имя переменной 'lessons' совпадает с related_name='lessons' в модели Lesson
    lessons = LessonSerializer(many=True, read_only=True)
    # Объявляем вычисляемое поле для общего количества уроков
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        # Явно перечисляем все поля, которые должны уйти в JSON
        fields = ('id', 'title', 'preview_image', 'description', 'lessons_count', 'lessons')

    def get_lessons_count(self, obj):
        # Считаем количество связанных уроков через backreference
        return obj.lessons.count()
