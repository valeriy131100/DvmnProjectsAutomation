import json
from tgbot.models import Student, ProjectManager
from django.core.management.base import BaseCommand


def create_manager(manager):
    current_manager, created = ProjectManager.objects.get_or_create(
        telegram_id=manager['telegram_id'],
        full_name=manager['name'],
    )
    current_manager.projects_time_begin = manager['projects_time_begin']
    current_manager.projects_time_end = manager['projects_time_end']
    current_manager.save()


def add_managers_to_db():
    with open(file='./PMs/managers.json') as file:
        managers = json.load(file)
        json.dumps(managers)
        for manager in managers:
            create_manager(manager)


def main():
    add_managers_to_db()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        main()
