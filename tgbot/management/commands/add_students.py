import json
import traceback
from tgbot.models import Student
from django.core.management.base import BaseCommand
import requests


def create_student(student):
    current_student, created = Student.objects.get_or_create(
        telegram_id=student['telegram_id'])
    current_student.full_name = student['name']
    current_student.skill_level = student['level']
    current_student.discord_username = student['discord_username']
    current_student.from_far_east = (student['is_far_east'])
    current_student.save()


def add_students_to_db(path):
    with open(path, encoding='utf-8') as file:
        students = json.load(file)
        json.dumps(students)
        for student in students:
            create_student(student)


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
            path = './Students/students.json'

        if not url:
            try:
                add_students_to_db(path)
            except FileNotFoundError:
                traceback.print_exc()
                print(f'\nФайл по пути {path} не найден')

        elif url:
            try:
                students = get_json(url)
                for student in students:
                    create_student(student)
            except Exception:
                traceback.print_exc()
                print('\nНе удалось загрузить json с указанного адреса')
