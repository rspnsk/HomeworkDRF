from rest_framework import serializers
from materials.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса."""
    class Meta:
        model = Course
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока."""
    class Meta:
        model = Lesson
        fields = '__all__'


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


class CourseDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального отображения курса со списком уроков и их количеством."""

    # 1. Вкладываем сериализатор уроков как список (многие к одному)
    # Имя переменной 'lessons' совпадает с related_name в модели Lesson
    lessons = LessonSerializer(many=True, read_only=True)

    # 2.  Добавляем кастомное поле для количества уроков
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'lessons_count', 'lessons')

    def get_lessons_count(self, obj):
        # Считаем количество связанных уроков
        return obj.lessons.count()
