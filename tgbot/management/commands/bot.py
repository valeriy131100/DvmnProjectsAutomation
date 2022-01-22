import os
from datetime import date, time, timedelta

import telegram
from django.core.management.base import BaseCommand
from django.db.models import Max, Min
from dotenv import load_dotenv
from telegram import (ForceReply, InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode, ReplyKeyboardRemove, Update, chat,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from tgbot.models import Student, Project, ProjectManager

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


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
        context.user_data['from_far_east'] = student.from_far_east
        buttons = ['Я в деле', 'Я не с вами']
        update.message.reply_text(
            f'Привет, {first_name}!\n\n'
            'Готовимся к новому проекту\n'
            f'Можешь пойти на проект с {start_date} или {second_start_date} \n\n'
            'Ты с нами?',
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
            'Вот это поворот! С тобой свяжется наш человек,'
            'чтобы выяснить обстоятельства.\n\n'
            'Если передумаешь, снова напиши /start',
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


def send_not(user_id):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(
        chat_id=user_id,
        text=f'Проект будет!',
    )


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

        conversation = ConversationHandler(
            entry_points=[CommandHandler('start', start_handler)],
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

        dispatcher.add_handler(conversation)
        # dispatcher.add_handler(constructor_handler)
        # dispatcher.add_handler(
        #     MessageHandler(filters=Filters.text, callback=show_orders))
        # dispatcher.add_handler(CommandHandler("help", help))

        updater.start_polling()
        updater.idle()
