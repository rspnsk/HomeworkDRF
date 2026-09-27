from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        # Проверяем, что пользователь авторизован, прежде чем смотреть группы
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем наличие пользователя в группе 'moderators'
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        # Если пользователь не авторизован, доступа нет
        if not request.user or not request.user.is_authenticated:
            return False
        # Проверяем, совпадает ли владелец объекта с текущим пользователем
        return obj.owner == request.user
