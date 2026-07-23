from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса."""
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'preview_image']


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока."""
    class Meta:
        model = Lesson
        fields = '__all__'