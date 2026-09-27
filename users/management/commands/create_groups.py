from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Создает группу модераторов в базе данных'

    def handle(self, *args, **options):
        group_name = 'moderators'
        group, created = Group.objects.get_or_create(name=group_name) # get_or_create = «найди или создай» — безопасный способ гарантировать наличие записи в базе.

        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" успешно создана!'))
        else:
            self.stdout.write(self.style.WARNING(f'Группа "{group_name}" уже существует.'))
