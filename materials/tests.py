from unittest.mock import patch

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser
from .models import Course, Lesson, Subscription


class MaterialsTestCase(APITestCase):

    def setUp(self):
        """Заполнение базы данных тестовыми данными перед каждым тестом."""
        # 1. Создаем группу модераторов
        self.moderators_group = Group.objects.create(name="moderators")

        # 2. Создаем пользователей
        self.user_owner = CustomUser.objects.create_user(
            email="owner@mail.ru", password="1234"
        )
        self.user_other = CustomUser.objects.create_user(
            email="other@mail.ru", password="1234"
        )
        self.user_moderator = CustomUser.objects.create_user(
            email="moder@mail.ru", password="1234"
        )
        # Добавляем модератора в группу
        self.user_moderator.groups.add(self.moderators_group)

        # 3. Создаем базовый курс и привязываем его к владельцу (user_owner)
        self.course = Course.objects.create(
            title="Основы Django",
            description="Изучаем Django REST Framework",
            owner=self.user_owner,
        )

        # 4. Создаем базовый урок и привязываем к владельцу
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Урок 1. Модели",
            description="Введение в ORM Django",
            video_link="https://youtube.com",
            owner=self.user_owner,
        )

 # ==================== ТЕСТЫ CRUD УРОКОВ ====================

    def test_create_lesson_by_owner(self):
        """Тест успешного создания урока обычным пользователем (владельцем)."""
        self.client.force_authenticate(user=self.user_owner)

        data = {
            "course": self.course.id,
            "title": "Урок 2. Сериализаторы",
            "description": "Изучаем сериализаторы в DRF",
            "video_link": "https://youtube.com",
        }

        url = reverse("materials:lesson-list-create")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        # Проверяем работу perform_create: owner должен привязаться автоматически
        self.assertEqual(Lesson.objects.last().owner, self.user_owner)

    def test_create_lesson_by_moderator_forbidden(self):
        """Тест: модератору запрещено создавать уроки (403)."""
        self.client.force_authenticate(user=self.user_moderator)

        data = {
            "course": self.course.id,
            "title": "Урок от модератора",
            "description": "Попытка спама",
            "video_link": "https://youtube.com",
        }

        url = reverse("materials:lesson-list-create")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json()["detail"], "Модераторам запрещено создавать уроки."
        )

    def test_create_lesson_validation_error(self):
        """Тест: валидатор блокирует ссылки на сторонние ресурсы (400)."""
        self.client.force_authenticate(user=self.user_owner)

        data = {
            "course": self.course.id,
            "title": "Урок с плохой ссылкой",
            "description": "Тест",
            "video_link": "https://wikipedia.org",  # Запрещенный домен
        }

        url = reverse("materials:lesson-list-create")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_link", response.json())

    def test_read_lesson_list(self):
        """Тест пагинации и получения списка: обычный юзер видит только свои уроки."""
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("materials:lesson-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что ответ структурирован пагинатором (есть ключ results)
        self.assertIn("results", response.json())
        self.assertEqual(len(response.json()["results"]), 1)

    def test_read_lesson_list_by_other_user(self):
        """Тест: другой пользователь видит пустой список, так как чужие уроки скрыты."""
        self.client.force_authenticate(user=self.user_other)
        url = reverse("materials:lesson-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)

    def test_update_lesson_by_owner(self):
        """Тест: владелец может успешно обновить свой урок."""
        self.client.force_authenticate(user=self.user_owner)

        data = {"title": "Обновленное название урока"}

        url = reverse(
            "materials:lesson-detail-update-delete", kwargs={"pk": self.lesson.pk}
        )
        response = self.client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Lesson.objects.get(pk=self.lesson.pk).title,
            "Обновленное название урока",
        )

    def test_delete_lesson_by_moderator_forbidden(self):
        """Тест: модератору запрещено удалять уроки (403)."""
        self.client.force_authenticate(user=self.user_moderator)

        url = reverse(
            "materials:lesson-detail-update-delete", kwargs={"pk": self.lesson.pk}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_by_owner(self):
        """Тест: владелец может успешно удалить свой урок."""
        self.client.force_authenticate(user=self.user_owner)

        url = reverse(
            "materials:lesson-detail-update-delete", kwargs={"pk": self.lesson.pk}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    # ==================== ТЕСТЫ ПОДПИСКИ НА ОБНОВЛЕНИЯ ====================

    def test_subscribe_to_course(self):
        """Тест: успешное создание подписки на курс (если её не было)."""
        self.client.force_authenticate(user=self.user_owner)

        # Полный путь соберется как /api/materials/courses/subscribe/
        url = reverse("materials:course-subscribe")
        data = {"course": self.course.id}

        # Изначально подписок в базе данных нет
        self.assertEqual(Subscription.objects.count(), 0)

        response = self.client.post(url, data=data, format='json')

        # Проверяем статус 201 CREATED и точный текст сообщения из контроллера
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["message"], "Подписка успешно установлена.")
        self.assertEqual(Subscription.objects.count(), 1)

        # Проверяем корректность связей в созданной подписке
        subscription = Subscription.objects.first()
        self.assertEqual(subscription.user, self.user_owner)
        self.assertEqual(subscription.course, self.course)

    def test_unsubscribe_from_course(self):
        """Тест: успешное удаление подписки при повторном запросе (отписка)."""
        self.client.force_authenticate(user=self.user_owner)

        # Предварительно создаем подписку в базе данных напрямую
        Subscription.objects.create(user=self.user_owner, course=self.course)
        self.assertEqual(Subscription.objects.count(), 1)

        url = reverse("materials:course-subscribe")
        data = {"course": self.course.id}

        response = self.client.post(url, data=data, format='json')

        # Проверяем статус 200 OK и точный текст удаления из контроллера
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Подписка успешно удалена.")
        self.assertEqual(Subscription.objects.count(), 0)

    def test_subscribe_to_non_existent_course(self):
        """Тест: попытка подписаться на несуществующий курс должна вернуть 404."""
        self.client.force_authenticate(user=self.user_owner)

        url = reverse("materials:course-subscribe")
        data = {"course": 99999}  # Несуществующий ID

        response = self.client.post(url, data=data, format='json')

        # Проверяем корректность работы get_object_or_404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
