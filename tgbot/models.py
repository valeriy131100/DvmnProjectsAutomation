import telegram
from projects_automation.settings import telegram_bot

from collections import defaultdict

from django.db import models
from datetime import datetime, timedelta

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


def check_slot_compatibility(student, slot):
    if slot:
        if not get_slot_lvl(slot) == student.get_lvl():
            return False
        for slot_student in slot:
            if slot_student in student.excluded_students.all():
                return False
            elif slot_student in student.excluded_by.all():
                return False

    return True


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

    # пары исключения
    excluded_students = models.ManyToManyField(
        'Student',
        verbose_name='Ученики с которыми не должен попасть',
        related_name='excluded_by',
        blank=True
    )

    excluded_pms = models.ManyToManyField(
        'ProjectManager',
        verbose_name='ПМ\'ы с которыми не должен попасть',
        related_name='excluded_by',
        blank=True
    )

    def __str__(self):
        return self.full_name

    def get_lvl(self):
        if self.skill_level in ('novice', 'novice+'):
            return 'novice'
        else:
            return 'junior'

    def send_cant_group_message(self, project_id, start_text):
        retry_message = (f'{start_text}\n'
                         f'Нажми на кнопку ниже, чтобы узнать варианты '
                         f'решения проблемы')

        retry_buttons = [
            [
                f'Посмотреть варианты в проекте {project_id}'
            ]
        ]
        try:
            telegram_bot.send_message(
                chat_id=self.telegram_id,
                text=retry_message,
                reply_markup=telegram.ReplyKeyboardMarkup(
                    retry_buttons,
                    resize_keyboard=True
                )
            )
        except telegram.error.BadRequest:
            pass

    def get_telegram_mention(self):
        return (f'<a href="tg://user?id={self.telegram_id}">'
                f'{self.full_name}</a>')

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
        verbose_name='Начало времени проектов',
        null=True
    )
    projects_time_end = models.TimeField(
        verbose_name='Конец времени проектов',
        null=True
    )

    def get_telegram_mention(self):
        return (f'<a href="tg://user?id={self.telegram_id}">'
                f'{self.full_name}</a>')

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

    def make_teams(self, week_num):
        pms = ProjectManager.objects.all()
        students = list(Student.objects.filter(preferred_week=week_num)
                                       .prefetch_related('excluded_by')
                                       .prefetch_related('excluded_students')
                                       .prefetch_related('excluded_pms'))
        for student in students:
            student.grouped = False

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

                    if pm in student.excluded_pms.all():
                        continue

                    begin_time = student.preferred_time_begin
                    end_time = student.preferred_time_end

                    if (begin_time is None) or (end_time is None):
                        # не зарегистрированных игнорируем
                        continue

                    if begin_time <= time_slot < end_time:
                        slot = slots_with_students[time_slot]
                        if not check_slot_compatibility(student, slot):
                            continue
                        slot.append(student)
                        student.grouped = True

            # наполняем дальневосточниками группы, где 1 человек
            for time_slot, slot_students in slots_with_students.items():
                if 0 < len(slot_students) < 2:
                    for student in students:
                        if student.from_far_east and not student.grouped:
                            if not check_slot_compatibility(student, slot_students):
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

            # если дальневосточники остались,
            # то дополняем команды из двух человек
            for time_slot, slot_students in slots_with_students.items():
                if len(slot_students) != 2:
                    continue

                for student in students:
                    if student.from_far_east and not student.grouped:
                        if not check_slot_compatibility(student, slot_students):
                            continue
                        slot_students.append(student)
                        student.grouped = True
                        break

            # создаем команды
            for time_slot, slot_students in slots_with_students.items():
                if len(slot_students) >= 2:
                    team = ProjectTeam.objects.create(
                        project=self,
                        project_manager=pm,
                        project_time=time_slot
                    )
                    team.students.set(slot_students)
                    team.save()

        # команды все еще состоящие из двух людей
        # если есть, то предлагаем их нераспределенным
        # не забудьте предложить только команды
        # у которых team.get_lvl() == student.get_lvl()

        still_not_full_teams = list(
            ProjectTeam.objects.filter(project=self)
                               .annotate(students_num=Count('students'))
                               .filter(students_num=2)
        )

        ungrouped_students = [
            student for student in students if not student.grouped
        ]

        teams = list(
            ProjectTeam.objects.filter(project=self)
        )

        for team in teams:
            team.send_notifications()

        for student in ungrouped_students:
            student.send_cant_group_message(
                self.id,
                start_text='Привет, к сожалению тебя не '
                           'удалось распределить в команды.'
            )


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

    def send_notifications(self):
        project_name = self.project.name

        participants_links = '\n'.join([
            student.get_telegram_mention()
            for student in self.students.all()
        ])

        pm = self.project_manager
        pm_link = pm.get_telegram_mention()

        project_time = self.project_time.isoformat(timespec="minutes")

        students_text = (
            f'Тебя успешно распределили на проект!\n'
            f'Собрание по проекту будет проходить в {project_time}\n\n'
            f'Твой проект-менеджер: {pm_link}\n'
            f'Твои коллеги: \n'
            f'{participants_links}'
        )

        students_buttons = [
            [
                f'Выйти из проекта {self.project.id}'
            ]
        ]

        for student in self.students.all():
            try:
                telegram_bot.send_message(
                    chat_id=student.telegram_id,
                    text=students_text,
                    parse_mode='HTML',
                    reply_markup=telegram.ReplyKeyboardMarkup(
                        students_buttons,
                        resize_keyboard=True
                    )
                )
            except telegram.error.BadRequest:
                continue

        pm_text = (
            f'Предварительный состав команды на {project_time}:\n\n'
            f'{participants_links}'
        )

        try:
            telegram_bot.send_message(
                chat_id=pm.telegram_id,
                text=pm_text,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest:
            pass

    class Meta:
        verbose_name = 'Команда проекта'
        verbose_name_plural = 'Команды проектов'
