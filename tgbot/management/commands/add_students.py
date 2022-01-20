import json
from tgbot.models import Student, ProjectManager, Project, SKILL_LEVEL_CHOICES
from django.core.management.base import BaseCommand


def is_far_east(student):
    return True if "True" in student else False


def create_student(student):
    current_student, created = Student.objects.get_or_create(
        telegram_id=student['telegram_id'])
    current_student.full_name = student['name']
    current_student.skill_level = student['level']
    current_student.discord_username = student['discord_username']
    current_student.from_far_east = (is_far_east(student['is_far_east']))
    current_student.save()


def add_students_to_db():
    with open(file='./Students/students.json') as file:
        students = json.load(file)
        json.dumps(students)
        for student in students:
            create_student(student)


def main():
    add_students_to_db()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        main()

