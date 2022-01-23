import json
from tgbot.models import ProjectManager
from django.core.management.base import BaseCommand
import requests


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


def get_json(url):
    response = requests.get(url)
    response.raise_for_status()
    students = response.json()

    return students


def main():
    add_managers_to_db()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("-j", "--json_path")

    def handle(self, *args, **options):
        url = options["json_path"]

        if not url:
            try:
                add_managers_to_db()
            except Exception as e:
                print(e, "\nВ папке PMs нет json файла")

        elif "http" in url:
            try:
                students = get_json(url)
                for student in students:
                    create_manager(student)
            except Exception as e:
                print(e, "\nАдрес указан неверно")
