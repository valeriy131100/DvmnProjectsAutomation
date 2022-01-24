import json
import traceback

import requests
from django.core.management.base import BaseCommand
from tgbot.models import ProjectManager


def create_manager(manager):
    current_manager, created = ProjectManager.objects.get_or_create(
        telegram_id=manager['telegram_id'],
        full_name=manager['name'],
    )
    current_manager.projects_time_begin = manager['projects_time_begin']
    current_manager.projects_time_end = manager['projects_time_end']
    current_manager.save()


def add_managers_to_db(path):
    with open(path, encoding='utf-8') as file:
        managers = json.load(file)
        json.dumps(managers)
        for manager in managers:
            create_manager(manager)


def get_json(url):
    response = requests.get(url)
    response.raise_for_status()
    json_ = response.json()

    return json_


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--url')
        parser.add_argument('-p', '--path')

    def handle(self, *args, **options):
        url = options['url']
        path = options['path']
        if not path:
            path = './PMs/managers.json'

        if not url:
            try:
                add_managers_to_db(path)
            except FileNotFoundError:
                traceback.print_exc()
                print(f'\nФайл по пути {path} не найден')

        elif url:
            try:
                students = get_json(url)
                for student in students:
                    create_manager(student)
            except Exception:
                traceback.print_exc()
                print('\nНе удалось загрузить json с указанного адреса')
