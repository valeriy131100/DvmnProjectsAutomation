import re
from datetime import date, time, timedelta

import telegram
from django.core.management.base import BaseCommand
from django.db.models import Max, Min
from telegram import (ReplyKeyboardRemove, Update, ReplyKeyboardMarkup)
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from projects_automation.settings import TELEGRAM_TOKEN, telegram_bot
from tgbot.models import Student, Project, ProjectManager, ProjectTeam
from django.db.models import Count


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def start_handler(update: Update, context: CallbackContext):

    project_id = context.args if context.args else None

    user_id = update.effective_chat.id
    start_date = Project.objects.all().only('project_date').first()
    start_date = start_date.project_date
    second_start_date = start_date + timedelta(days=7)

    context.user_data['start_date'] = start_date
    context.user_data['second_start_date'] = second_start_date

    student = Student.objects.get(telegram_id=user_id)
    first_name = update.effective_chat.first_name

    if not student:
        update.message.reply_text(
            f'Привет, {first_name}!\n\n'
            'К сожалению, не вижу тебя в списке студентов \n'
            'Чтобы стать крутым разработчиком, иди на https://dvmn.org 🎁\n\n'
            'Как только станешь студентом, еще раз напиши /start',
        )

        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Привет, пока еще рано, мы напишем тебе, когда нужно будет '
            'регистрироваться!'
        )


def project_start_handler(update: Update, context: CallbackContext):
    text = update.message.text
    s_project_id = re.match(r'^Регистрация на проект (\d+)$', text).groups()[0]
    project_id = int(s_project_id)

    user_id = update.effective_chat.id
    start_date = Project.objects.get(id=project_id)
    start_date = start_date.project_date
    second_start_date = start_date + timedelta(days=7)

    context.user_data['start_date'] = start_date
    context.user_data['second_start_date'] = second_start_date

    student = Student.objects.get(telegram_id=user_id)
    first_name = update.effective_chat.first_name

    context.user_data['from_far_east'] = student.from_far_east
    buttons = ['Я в деле', 'Я не с вами']
    update.message.reply_text(
        f'Можешь пойти на проект с {start_date} или {second_start_date} \n\n'
        'Ты с нами?\n',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=build_menu(buttons, n_cols=2),
            resize_keyboard=True
        ),
    )
    return 'choose_week'


def choose_week(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    text = update.message.text

    project_dates = [
        str(context.user_data['start_date']),
        str(context.user_data['second_start_date'])
    ]

    if text == 'Я в деле':
        update.message.reply_text(
            'Отлично, на какую неделю тебя записать?\n\n'

            f'Можешь пойти на проект: \n\n',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=build_menu(project_dates, n_cols=2),
                resize_keyboard=True
            ),
        )

        return 'choose_time'
    elif text == 'Я не с вами':
        update.message.reply_text(
            'Вот это поворот! Напиши, пожалуйста, '
            'куратору и уточни в чем дело',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


def choose_time(update: Update, context: CallbackContext):
    buttons = []
    text = update.message.text
    user_id = update.effective_chat.id
    student = Student.objects.get(telegram_id=user_id)
    student.project_date = date.fromisoformat(text)
    student.save()

    available_time = ProjectManager.objects.all().aggregate(
        start_time=Min('projects_time_begin'),
        end_time=Max('projects_time_end')
    )
    min_available_time = time.strftime(available_time['start_time'], '%H:%M')
    max_available_time = time.strftime(available_time['end_time'], '%H:%M')

    project_managers = ProjectManager.objects.all()
    for manager in project_managers:
        buttons += [str(meeting_time) for meeting_time in manager.get_time_slots()]
    buttons = list(dict.fromkeys(buttons))

    if context.user_data['from_far_east']:
        update.message.reply_text(
            'В какое время тебе было бы удобно созваниваться с ПМом? (время для ДВ) '
            '(время указано по МСК)',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=build_menu(buttons, n_cols=5),
                resize_keyboard=True
            ))

        return 'write_time_to_db'

    else:
        update.message.reply_text(

            'Созвоны с ПМом и командой будут проходить каждый день, '
            'кроме субботы и воскресенья. '
            'И будут длиться примерно 30 мин. \n\n'
            'В какое время тебе было бы удобно созваниваться с ПМом? '
            f'В интервале с  {min_available_time} по {max_available_time} '
            '(время указано по МСК) \n\n'
            f'* Указать удобное время необходимо в формате {min_available_time}-{max_available_time}',
            reply_markup=ReplyKeyboardRemove()
        )

        return 'write_time_to_db'


def send_project_registration(telegram_id, project_id):

    keyboard = [
        [
            f'Регистрация на проект {project_id}'
        ]
    ]

    try:
        telegram_bot.send_message(
            chat_id=telegram_id,
            text='Привет! Снова пришла пора проектов. Нажми на кнопку ниже '
                 'если ты готов начать регистрацию',
            reply_markup=ReplyKeyboardMarkup(keyboard)
        )
    except telegram.error.BadRequest:
        pass


def write_time_to_db(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    text = update.message.text
    if "-" not in text or len(text) < 10 or "." in text:
        update.message.reply_text(
            'Введите удобное время созвонов в формате 18:00-00:00',
            reply_markup=ReplyKeyboardRemove()
        )
        return

    preferred_time_begin, preferred_time_end = text.split('-')
    preferred_time_begin = time.fromisoformat(preferred_time_begin)
    preferred_time_end = time.fromisoformat(preferred_time_end)
    student = Student.objects.get(telegram_id=user_id)
    student.preferred_time_end = preferred_time_end
    student.preferred_time_begin = preferred_time_begin
    student.save()

    update.message.reply_text(
        'После распределения групп вам придет сообщение со временем созвонов '
        'и составом группы!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def retry_start_handler(update: Update, context: CallbackContext):
    text = update.message.text

    match = re.match(r'^Посмотреть варианты в проекте (\d+)$', text)
    if match:
        s_project_id = match.groups()[0]
        project_id = int(s_project_id)
        context.user_data['project_id'] = project_id
    else:
        project_id = context.user_data.get('project_id', None)

    still_not_full_teams = list(
        ProjectTeam.objects.filter(project__pk=project_id)
                           .annotate(students_num=Count('students'))
                           .filter(students_num=2)
    )

    student = Student.objects.get(telegram_id=update.message.from_user.id)

    buttons = [
        [f'Записаться в команду {team.id} '
         f'(собрания в {team.project_time.isoformat(timespec="minutes")})']
        for team in still_not_full_teams
        if team.get_lvl() == student.get_lvl()
    ]

    if student.preferred_week == 1:
        buttons.append(
            ['Попробовать попасть в команду на следующей неделе']
        )

    if len(buttons) > 0:
        update.message.reply_text(
            'Доступны следующие варианты',
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True
            )
        )
        return 'retry_answer'
    else:
        update.message.reply_text(
            'Кажется у нас совершенно нет вариантов, '
            'чтобы ты попал на проект. '
            'Спроси у своего куратора, что тебе стоит делать',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


def retry_add_team_handler(update: Update, context: CallbackContext):
    student = Student.objects.get(telegram_id=update.message.from_user.id)

    text = update.message.text

    team_id = re.match(
        r'^Записаться в команду (\d+)',
        text
    ).groups()[0]
    team = ProjectTeam.objects.get(pk=int(team_id))

    if team.students.count() == 3:
        update.message.reply_text(
            'Извините, но с момента прошлого сообщения кто-то уже успел '
            'попасть в эту команду.'
        )
        return retry_start_handler(update, context)
    else:
        team.students.add(student)
        team.save()

        project_id = context.user_data['project_id']
        project = Project.objects.get(pk=project_id)

        project_name = project.name

        participants_links = '\n'.join([
            f'<a href="tg://user?id={team_student.telegram_id}">'
            f'{team_student.full_name}</a>'
            for team_student in team.students.all()
        ])

        student_link = (
            f'<a href="tg://user?id={student.telegram_id}">'
            f'{student.full_name}</a>'
        )

        pm = team.project_manager
        pm_link = f'<a href="tg://user?id={pm.telegram_id}">{pm.full_name}</a>'

        project_time = team.project_time.isoformat(timespec="minutes")

        text = (
            f'Успешно!\n'
            f'Собрание по проекту будет проходить в {project_time}\n\n'
            f'Твой проект-менеджер: {pm_link}\n'
            f'Твои коллеги: \n'
            f'{participants_links}'
        )

        update.message.reply_text(
            text,
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove()
        )

        pm = team.project_manager

        pm_text = (
            f'В команду на {project_time} добавился ученик {student_link}'
        )

        try:
            telegram_bot.send_message(
                chat_id=pm.telegram_id,
                text=pm_text,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest:
            pass

        return ConversationHandler.END


def retry_change_week_handler(update: Update, context: CallbackContext):
    student = Student.objects.get(telegram_id=update.message.from_user.id)
    student.preferred_week = 2
    student.save()

    update.message.reply_text(
        'До встречи на следующей неделе!',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    """Cancel and end the conversation."""
    update.message.reply_text(
        'Всего доброго!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


class Command(BaseCommand):
    help = 'Бот для записи участников на проект и их распределения по группам'

    def handle(self, *args, **kwargs):
        updater = Updater(TELEGRAM_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        reg_conversation = ConversationHandler(
            entry_points=[
                MessageHandler(
                    Filters.regex(r'^Регистрация на проект \d+$'),
                    project_start_handler,
                    pass_user_data=True
                )],
            states={
                'choose_week': [
                    MessageHandler(
                        Filters.text,
                        choose_week,
                        pass_user_data=True
                    )
                ],
                'choose_time': [
                    MessageHandler(
                        Filters.text,
                        choose_time,
                        pass_user_data=True
                    )
                ],
                'write_time_to_db': [
                    MessageHandler(
                        Filters.text,
                        write_time_to_db,
                        pass_user_data=True
                    )
                ]
            },
            per_user=True,
            fallbacks=[
                CommandHandler('cancel', cancel)],
        )

        retry_conversation = ConversationHandler(
            entry_points=[
                MessageHandler(
                    Filters.regex(r'^Посмотреть варианты в проекте \d+$'),
                    retry_start_handler,
                    pass_user_data=True
                )],
            states={
                'retry_answer': [
                    MessageHandler(
                        Filters.regex(r'^Записаться в команду \d+'
                                      r' \(собрания в \d{2}:\d{2}\)$'),
                        retry_add_team_handler,
                        pass_user_data=True
                    ),
                    MessageHandler(
                        Filters.regex(r'^Попробовать попасть в'
                                      r' команду на следующей неделе$'),
                        retry_change_week_handler,
                        pass_user_data=True
                    )
                ]
            },
            per_user=True,
            fallbacks=[]
        )

        dispatcher.add_handler(reg_conversation)
        dispatcher.add_handler(retry_conversation)
        dispatcher.add_handler(CommandHandler('start', start_handler))
        # dispatcher.add_handler(constructor_handler)
        # dispatcher.add_handler(
        #     MessageHandler(filters=Filters.text, callback=show_orders))
        # dispatcher.add_handler(CommandHandler("help", help))

        updater.start_polling()
        updater.idle()
