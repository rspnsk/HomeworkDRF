from users.models import CustomUser
from .models import Course, Lesson, Subscription

from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import  Payment


class MaterialsTestCase(APITestCase):

    def setUp(self):
        """Заполнение базы данных тестовыми данными перед каждым тестом."""
        # 1. Создаем группу модераторов
        self.moderators_group, _ = Group.objects.get_or_create(name="moderators")

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

    @patch('materials.tasks.send_course_update_email.delay')
    def test_notification_triggered_on_lesson_creation(self, mock_send_email):
        """Тест: при добавлении нового урока подписчики курса получают уведомление."""
        # 1. Оформляем подписку для другого пользователя (user_other) на наш курс
        Subscription.objects.create(user=self.user_other, course=self.course)

        # 2. Авторизуем владельца курса для добавления нового урока
        self.client.force_authenticate(user=self.user_owner)

        data = {
            "course": self.course.id,
            "title": "Урок 3. Тестирование",
            "description": "Проверяем триггер отправки email",
            "video_link": "https://youtube.com",
        }

        # 3. Отправляем POST-запрос на создание урока
        url = reverse("materials:lesson-list-create")
        response = self.client.post(url, data=data, format='json')

        # 4. Проверяем, что урок успешно создался
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 5. Проверяем, что фоновая задача Celery была вызвана ровно 1 раз с ID нашего курса
        mock_send_email.assert_called_once_with(self.course.id)

    @patch('materials.tasks.send_course_update_email.delay')
    def test_notification_triggered_on_course_update(self, mock_send_email):
        """Тест: при обновлении курса через API подписчики получают уведомление."""
        # 1. Оформляем подписку для другого пользователя (user_other) на наш курс
        Subscription.objects.create(user=self.user_other, course=self.course)

        # 2. Авторизуем владельца курса для редактирования
        self.client.force_authenticate(user=self.user_owner)

        # Данные для частичного обновления курса (PATCH)
        data = {
            "description": "Новое обновленное описание курса с актуальной информацией."
        }

        # 3. Отправляем PATCH-запрос на эндпоинт деталей курса (CourseViewSet - action: partial_update)
        # Имя роута для ViewSet по умолчанию формируется как 'basename-detail'
        url = reverse("materials:course-detail", kwargs={"pk": self.course.pk})
        response = self.client.patch(url, data=data, format='json')

        # 4. Проверяем, что запрос прошел успешно (200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что описание действительно обновилось в базе данных
        self.course.refresh_from_db()
        self.assertEqual(self.course.description, "Новое обновленное описание курса с актуальной информацией.")

        # 5. Проверяем, что фоновая задача Celery была вызвана ровно 1 раз с ID нашего курса
        mock_send_email.assert_called_once_with(self.course.id)


User = get_user_model()


class PaymentStripeTestCase(APITestCase):

    def setUp(self):
        """Заполнение базы данных тестовыми данными перед каждым тестом."""
        self.user = User.objects.create_user(
            email="student@mail.ru",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title="Курс по Django и Stripe",
            description="Изучаем платежи",
            price=2500.00,
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Урок 1. Интеграция Stripe",
            description="Практика",
            video_link="https://youtube.com",
            price=700.00,
            owner=self.user
        )

    @patch('users.views.create_stripe_session')
    @patch('users.views.create_stripe_price')
    @patch('users.views.create_stripe_product')
    def test_create_stripe_payment_for_course(self, mock_create_product, mock_create_price, mock_create_session):
        """Тест: успешное создание платежа за КУРС с генерацией ссылки Stripe."""

        # Настраиваем фейковые ответы от сервисных функций
        mock_create_product.return_value = "prod_fake123"
        mock_create_price.return_value = "price_fake123"
        mock_create_session.return_value = ("cs_test_fake123", "https://stripe.com")

        url = reverse("users:payment-create")
        data = {
            "paid_course": self.course.id,
            "payment_method": "stripe"
        }

        response = self.client.post(url, data=data, format='json')

        # Проверяем успешность ответа API
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["session_id"], "cs_test_fake123")
        self.assertEqual(response.data["payment_url"], "https://stripe.com")
        self.assertEqual(float(response.data["payment_amount"]), 2500.00)
        self.assertEqual(response.data["status"], "created")

    @patch('users.views.retrieve_stripe_session_status')
    def test_retrieve_payment_status_updated_to_paid(self, mock_retrieve_status):
        """Тест: ручной эндпоинт проверки меняет статус на Оплачено, если Stripe подтвердил платеж."""

        payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            payment_amount=2500.00,
            payment_method="stripe",
            session_id="cs_test_fake123",
            payment_url="https://stripe.com",
            status="created"
        )

        # Симулируем ответ от нашего сервиса проверки статуса
        mock_retrieve_status.return_value = "paid"

        url = reverse("users:payment-status", kwargs={"pk": payment.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "paid")

        # Проверяем обновление статуса в базе данных
        payment.refresh_from_db()
        self.assertEqual(payment.status, "paid")
