from django.db import models

SKILL_LEVEL_CHOICES = [
    ('novice', 'Новичок'),
    ('novice+', 'Новичок+'),
    ('junior', 'Джун')
]


class Student(models.Model):
    telegram_id = models.IntegerField(
        verbose_name='ID в telegram',
        blank=True,
        null=True
    )
    telegram_username = models.CharField(
        verbose_name='Username в telegram',
        max_length=100,
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

    class Meta:
        verbose_name = 'ПМ'
        verbose_name_plural = 'ПМы'


class Project(models.Model):
    name = models.CharField(max_length=100)


class ProjectTeam(models.Model):
    project = models.ForeignKey(
        Project,
        related_name='teams',
        on_delete=models.CASCADE
    )
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

