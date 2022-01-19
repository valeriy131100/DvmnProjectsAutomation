from django.db import models

SKILL_LEVEL_CHOICES = [
    ('beginner', 'Новичок'),
    ('advanced', 'Новичок+'),
    ('junior', 'Джун')
]


class Student(models.Model):
    telegram_id = models.IntegerField(
        verbose_name='ID в telegram',
        primary_key=True
    )
    full_name = models.CharField(
        verbose_name='ФИО',
        max_length=200
    )
    skill_level = models.CharField(
        verbose_name='Уровень навыков',
        choices=SKILL_LEVEL_CHOICES,
        max_length=50
    )
    from_far_east = models.BooleanField(
        verbose_name='С Дальнего Востока',
        default=False
    )

    preferred_time_begin = models.TimeField(
        verbose_name='Предпочитаемое начало времени проектов',
        null=True,
        blank=True
    )
    preferred_time_end = models.TimeField(
        verbose_name='Предпочитаемый конец времени проектов',
        null=True,
        blank=True
    )


class ProjectManager(models.Model):
    telegram_id = models.IntegerField(
        verbose_name='ID в telegram',
        primary_key=True
    )
    full_name = models.CharField(
        verbose_name='ФИО',
        max_length=200
    )

    projects_time_begin = models.TimeField(
        verbose_name='Начало времени проектов'
    )
    projects_time_end = models.TimeField(
        verbose_name='Конец времени проектов'
    )


class Project(models.Model):
    project_manager = models.ForeignKey(
        ProjectManager,
        related_name='projects',
        on_delete=models.CASCADE
    )
    students = models.ManyToManyField(
        Student,
        related_name='projects',
        verbose_name='Участники проекта'
    )

    project_time = models.TimeField(
        verbose_name='Время собрания по проектам'
    )

