import json
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


def add_students_to_db():
    with open(file='./Students/students.json', encoding='utf-8') as file:
        students = json.load(file)
        json.dumps(students)
        for student in students:
            create_student(student)


def get_json(url):
    response = requests.get(url)
    response.raise_for_status()
    students = response.json()

    return students


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("-j", "--json_path")

    def handle(self, *args, **options):
        url = options["json_path"]

        if not url:
            try:
                add_students_to_db()
            except FileNotFoundError as e:
                print(e, "\nВ папке Students нет json файла")

        elif "http" in url:
            try:
                students = get_json(url)
                for student in students:
                    create_student(student)
            except Exception as e:
                print(e, "\nАдрес указан неверно")
