from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateAPI, LessonRetrieveUpdateDeleteAPI

app_name = "materials"

# Настройка роутера для ViewSet (курсы)
router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("", include(router.urls)),

    path("lessons/", LessonListCreateAPI.as_view(), name="lesson-list-create"),
    path("lessons/<int:pk>/", LessonRetrieveUpdateDeleteAPI.as_view(), name="lesson-detail-update-delete"),
]

# /api/courses/ — Список курсов и создание нового.
# /api/courses/{id}/ — Деталь курса, его изменение и удаление.
# /api/lessons/ — Список всех уроков и создание нового.
# /api/lessons/{id}/ — Деталь урока, его изменение и удаление.
