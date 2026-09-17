import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import Payment, CustomUser
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Заполняет таблицу платежей данными из JSON-файла'

    def handle(self, *args, **options):
        # 1. Очищаем старые платежи
        Payment.objects.all().delete()

        # 2. Получаем объекты из базы для связи
        user = CustomUser.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user or not course or not lesson:
            self.stdout.write(self.style.ERROR('В базе данных не хватает пользователей, курсов или уроков!'))
            return

        # 3. Путь к файлу JSON (динамически собираем путь внутри приложения users)
        json_path = os.path.join(settings.BASE_DIR, 'users', 'data', 'payments.json')

        try:
            # 4. Читаем данные из файла
            with open(json_path, 'r', encoding='utf-8') as file:
                payments_data = json.load(file)

            # 5. Перебираем данные и добавляем связи динамически
            # Для первого платежа (индекс 0) привяжем курс, для второго (индекс 1) — урок
            for index, payment_info in enumerate(payments_data):
                if index == 0:
                    payment_info['user'] = user
                    payment_info['paid_course'] = course
                    payment_info['paid_lesson'] = None
                else:
                    payment_info['user'] = user
                    payment_info['paid_course'] = None
                    payment_info['paid_lesson'] = lesson

                # Создаем запись в базе данных
                Payment.objects.create(**payment_info)

            self.stdout.write(self.style.SUCCESS('Данные из JSON успешно загружены в таблицу платежей!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден по пути: {json_path}'))

