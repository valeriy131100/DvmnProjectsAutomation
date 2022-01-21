from django.db import models
from datetime import datetime, timedelta
import calendar

SKILL_LEVEL_CHOICES = [
    ('novice', 'Новичок'),
    ('novice+', 'Новичок+'),
    ('junior', 'Джун')
]


WEEK_CHOICES = [
    (3, 'Третья неделя месяца'),
    (4, 'Четвертая неделя месяца')
]


class Student(models.Model):
    telegram_id = models.IntegerField(
        verbose_name='ID в telegram',
        primary_key=True
    )
    discord_username = models.CharField(
        verbose_name='Username в discord',
        max_length=100,
        blank=True
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

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


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

    def __str__(self):
        return self.full_name

    def get_time_slots(self):
        start_time = self.projects_time_begin
        end_time = self.projects_time_end
        start_date = datetime.now().replace(
            hour=start_time.hour,
            minute=start_time.minute,
            second=0,
            microsecond=0
        )
        if end_time.hour > start_date.hour:
            end_date = datetime.now()
        else:
            end_date = datetime.now()
            end_date = end_date.replace(day=end_date.day + 1)
        end_date = end_date.replace(
            hour=end_time.hour,
            minute=end_time.minute,
            second=0,
            microsecond=0
        )

        delta = end_date - start_date
        minutes_delta = delta.seconds // 60
        minutes_ranges = [i * 30 for i in range(minutes_delta // 30)]
        time_ranges = [
            (start_date + timedelta(minutes=minute_range)).time()
            for minute_range in minutes_ranges
        ]

        return time_ranges

    class Meta:
        verbose_name = 'ПМ'
        verbose_name_plural = 'ПМы'


class Project(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Проект')

    project_date = models.DateField(
        verbose_name='Дата начала проекта',
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class ProjectTeam(models.Model):
    project = models.ForeignKey(
        Project,
        related_name='teams',
        on_delete=models.CASCADE,
        verbose_name='Проект'
    )
    project_manager = models.ForeignKey(
        ProjectManager,
        related_name='projects',
        on_delete=models.CASCADE,
        verbose_name='ПМ'
    )
    students = models.ManyToManyField(
        Student,
        related_name='projects',
        verbose_name='Участники проекта'
    )

    project_time = models.TimeField(
        verbose_name='Время собрания по проектам'
    )

    def __str__(self):
        return f'{self.id} команда проекта "{self.project.name}"'

    class Meta:
        verbose_name = 'Команда проекта'
        verbose_name_plural = 'Команды проектов'
