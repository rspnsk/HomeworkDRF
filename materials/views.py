from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer, CourseDetailSerializer
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied  # Импортируем ошибку 403
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """ Контроллер для Курсов """

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        """Модераторы видят все курсы, обычные пользователи — только свои."""
        user = self.request.user

        # 1. Если зашел модератор, отдаем вообще ВСЕ курсы из базы (с prefetch_related)
        if user.is_authenticated and user.groups.filter(name='moderators').exists():
            return Course.objects.prefetch_related('lessons').all()

        # 2. Если зашел обычный юзер, фильтруем по владельцу (тоже с prefetch_related)
        return Course.objects.filter(owner=user).prefetch_related('lessons')

    def perform_create(self, serializer):
        """Автоматически привязывает текущего пользователя как владельца курса."""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """Разграничение прав для модераторов и владельцев."""
        user = self.request.user
        is_moderator = user.is_authenticated and user.groups.filter(name='moderators').exists()

        # 1. Создание: модераторам нельзя, обычным авторизованным можно
        if self.action == 'create':
            if is_moderator:
                raise PermissionDenied("Модераторам запрещено создавать курсы.")
            return [IsAuthenticated()]

        # 2. Удаление: модераторам нельзя, обычным пользователям можно ТОЛЬКО СВОЁ
        elif self.action == 'destroy':
            if is_moderator:
                raise PermissionDenied("Модераторам запрещено удалять курсы.")
            return [IsAuthenticated(), IsOwner()]

        # 3. Просмотр детали и редактирование: можно модератору ИЛИ владельцу
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Если это не модератор, то строго требуем быть владельцем
            if not is_moderator:
                return [IsAuthenticated(), IsOwner()]
            return [IsAuthenticated()]

        # 4. Просмотр списка (list)
        return [IsAuthenticated()]


class LessonListCreateAPI(generics.ListCreateAPIView):
    """ Список уроков и Создание урока """
    serializer_class = LessonSerializer

    def get_queryset(self):
        """Модераторы видят все уроки, обычные пользователи — только свои."""
        user = self.request.user
        if user.is_authenticated and user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Автоматическая привязка владельца при создании урока."""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            if self.request.user.is_authenticated and self.request.user.groups.filter(name='moderators').exists():
                raise PermissionDenied("Модераторам запрещено создавать уроки.")
        return [IsAuthenticated()]


class LessonRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    """ Просмотр детали, Изменение и Удаление урока """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        user = self.request.user
        is_moderator = user.is_authenticated and user.groups.filter(name='moderators').exists()

        # На удаление модератору нельзя, а обычному юзеру можно только своё
        if self.request.method == 'DELETE':
            if is_moderator:
                raise PermissionDenied("Модераторам запрещено удалять уроки.")
            return [IsAuthenticated(), IsOwner()]

        # На просмотр детали и редактирование (PUT/PATCH): если не модератор, требуем IsOwner
        elif self.request.method in ['GET', 'PUT', 'PATCH']:
            if not is_moderator:
                return [IsAuthenticated(), IsOwner()]

        return [IsAuthenticated()]