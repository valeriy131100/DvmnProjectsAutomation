import os
from datetime import datetime, date, time, timedelta
from pprint import pprint


from django.core.management.base import BaseCommand
from django.db.models import Max, Min
from dotenv import load_dotenv
from telegram import (ForceReply, InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode, ReplyKeyboardRemove, Update, chat,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from tgbot.models import WEEK_CHOICES, Student, ProjectManager

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def start_handler(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    project_start = WEEK_CHOICES

    student = Student.objects.get(telegram_id=user_id)
    first_name = update.effective_chat.first_name

    if not student:
        update.message.reply_text(
            f'Привет, {first_name}!\n\n'
            'К сожалению? не вижу тебя в списке студентов \n'
            'Чтобы стать крутым разработчиком, иди на https://dvmn.org 🎁\n\n'
            'Как только станешь студентом, еще раз напиши /start',
        )

        return ConversationHandler.END

    else:
        if str(datetime.now()) > str(project_start[1][1]):
            update.message.reply_text(
                f'Привет, {first_name}!\n\n'
                f'К сожалению, все проекты уже стартовали.'
                'Жди проект в следующем месяце\n'
            )
            # add remove third week if datetime.now > third week
            return ConversationHandler.END

        else:
            context.user_data['from_far_east'] = student.from_far_east
            update.message.reply_text(
                f'Привет, {first_name}!\n\n'
                'Готовимся к новому проекту\n'
                f'Можешь пойти на проект с {project_start[0][1]} или {project_start[1][1]} \n\n'
                'Ты с нами?',
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text='Я в деле'),
                            KeyboardButton(text='Я не с вами')
                        ],
                    ],
                    resize_keyboard=True
                ),
            )
        return 'choose_week'


def choose_week(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    text = update.message.text

    project_start = WEEK_CHOICES

    if text == 'Я в деле':
        update.message.reply_text(
            'Отлично, на какую неделю тебя записать?\n\n'

            f'Можешь пойти на проект с {project_start[0][1]} или c {project_start[1][1]} \n\n'
            'Ты с нами?',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text=project_start[0][1]),
                        KeyboardButton(text=project_start[1][1])
                    ],
                ],
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
    # add if text != 'Назад' to enable week change
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

    if context.user_data['from_far_east']:
        update.message.reply_text(
            'В какое время тебе было бы удобно созваниваться с ПМом? (время для ДВ) '
            '(время указано по МСК)',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='10:00-10:30'),
                        KeyboardButton(text='10:30-11:00'),
                        KeyboardButton(text='11:00-11:30'),
                        KeyboardButton(text='11:30-12:00'),
                    ],
                ],
                resize_keyboard=True
            ))

        return 'write_time_to_db'

    else:
        update.message.reply_text(
            'Созвоны с ПМом и командой будут проходить каждый день,'
            'кроме субботы и воскресенья.' 
            'И будут длиться примерно 30 мин \n\n'
            'В какое время тебе было бы удобно созваниваться с ПМом?'
            f'В интервале с  {min_available_time} по {max_available_time} '
            '(время указано по МСК) \n\n'
            f'* Указать удобное время необходимо в формате {min_available_time}-{max_available_time}',
            reply_markup=ReplyKeyboardRemove()
        )

        return 'write_time_to_db'


def write_time_to_db(update: Update, context: CallbackContext):

    user_id = update.effective_chat.id
    text = update.message.text
    preferred_time_begin, preferred_time_end = text.split('-')
    preferred_time_begin = time.fromisoformat(preferred_time_begin)
    preferred_time_end = time.fromisoformat(preferred_time_end)
    student = Student.objects.get(telegram_id=user_id)
    student.preferred_time_end = preferred_time_end
    student.preferred_time_begin = preferred_time_begin
    student.save()

    update.message.reply_text(
        'После распределения групп вам придет сообщение со временем соззвонов'
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
