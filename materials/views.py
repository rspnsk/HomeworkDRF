from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(ModelViewSet):
    """ (DRY-подход). Предоставляет полный набор действий для работы с курсами:
    получение списка, просмотр детали, создание, обновление и удаление. """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonListCreateAPI(ListCreateAPIView):
    """ Получение списка всех уроков ИЛИ Создание нового урока. """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDeleteAPI(RetrieveUpdateDestroyAPIView):
    """ Просмотр одного конкретного урока, его изменение или удаление. """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
