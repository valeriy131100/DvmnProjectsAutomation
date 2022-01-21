from collections import defaultdict

from django.db import models
from datetime import datetime, timedelta
import calendar

from django.db.models import Count

SKILL_LEVEL_CHOICES = [
    ('novice', 'Новичок'),
    ('novice+', 'Новичок+'),
    ('junior', 'Джун')
]


WEEK_CHOICES = [
    (1, 'Первая неделя'),
    (2, 'Вторая неделя')
]


def get_slot_lvl(slot):
    student = slot[0]
    return student.get_lvl()


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

    preferred_week = models.IntegerField(
        verbose_name='Предпочитаемая неделя проекта',
        choices=WEEK_CHOICES,
        default=1
    )

    def __str__(self):
        return self.full_name

    def get_lvl(self):
        if self.skill_level in ('novice', 'novice+'):
            return 'novice'
        else:
            return 'junior'

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
    MAX_WEEK_NUM = 2

    name = models.CharField(
        max_length=100,
        verbose_name='Проект')

    project_date = models.DateField(
        verbose_name='Дата начала проекта',
        blank=True
    )

    current_week = models.IntegerField(
        verbose_name='Текущая неделя проекта',
        choices=WEEK_CHOICES,
        default=1
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def make_teams(self):
        current_week = self.current_week
        pms = ProjectManager.objects.all()
        students = list(Student.objects.filter(preferred_week=current_week))
        for student in students:
            student.grouped = False

        print(students)
        for pm in pms:
            time_slots = pm.get_time_slots()
            slots_with_students = defaultdict(list)
            for time_slot in time_slots:
                if len(slots_with_students[time_slot]) == 3:
                    continue

                for student in students:
                    if student.grouped:
                        continue

                    if student.from_far_east:
                        continue

                    begin_time = student.preferred_time_begin
                    end_time = student.preferred_time_end

                    if (begin_time is None) or (end_time is None):
                        # не зарегистрированных игнорируем
                        continue

                    if begin_time <= time_slot < end_time:
                        slot = slots_with_students[time_slot]
                        if slot:
                            if not get_slot_lvl(slot) == student.get_lvl():
                                continue
                        slot.append(student)
                        student.grouped = True

            for time_slot, slot_students in slots_with_students.items():
                if len(slot_students) == 0:
                    continue
                if 0 < len(slot_students) < 2:
                    for student in students:
                        if student.from_far_east and not student.grouped:
                            if not get_slot_lvl(slot_students) == student.get_lvl():
                                continue
                            slot_students.append(student)
                            student.grouped = True
                            break
                    else:
                        # если не удалось наполнить дальневосточниками,
                        # то пропускаем и ставим негруппированность
                        for student in slot_students:
                            student.grouped = False
                        continue
                team = ProjectTeam.objects.create(
                    project=self,
                    project_manager=pm,
                    project_time=time_slot
                )
                team.students.set(slot_students)
                team.save()

        # если дальневосточники остались,
        # то дополняем команды из двух человек
        not_full_teams = list(ProjectTeam.objects.annotate(
            students_num=Count('students')
        ).filter(students_num=2))

        for team in not_full_teams:
            for student in students:
                if student.from_far_east and not student.grouped:
                    if student.get_lvl() != team.get_lvl():
                        continue
                    team.students.add(student)
                    student.grouped = True
                    break

        # команды все еще состоящие из двух людей
        # если есть, то предлагаем их нераспределенным
        # не забудьте предложить только команды
        # у которых team.get_lvl() == student.get_lvl()

        still_not_full_teams = list(ProjectTeam.objects.annotate(
            students_num=Count('students')
        ).filter(students_num=2))

        ungrouped_students = [
            student for student in students if not student.grouped
        ]

        print(still_not_full_teams, ungrouped_students)


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

    def get_lvl(self):
        return self.students.all()[0].get_lvl()

    def notifications(self):
        students = self.students
        print(students)


    class Meta:
        verbose_name = 'Команда проекта'
        verbose_name_plural = 'Команды проектов'
