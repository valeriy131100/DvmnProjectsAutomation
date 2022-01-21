import os
from datetime import datetime, date

from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram import (ForceReply, InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode, ReplyKeyboardRemove, Update, chat,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from tgbot.models import WEEK_CHOICES, Student
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
        # add write week to db. week should be associated with user_id
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
    if context.user_data['from_far_east']:
        update.message.reply_text(
            'В какое время тебе было бы удобно созваниваться с ПМом? (время для ДВ) '
            '(время указано по МСК)',
            reply_markup=ReplyKeyboardRemove()
            # chose time between 18-21
        )
    else:
        update.message.reply_text(
            'В какое время тебе было бы удобно созваниваться с ПМом? (время для ЦРРФ)'
            '(время указано по МСК)',
            reply_markup=ReplyKeyboardRemove()
            # chose time between 18-21
        )


    # add write time to DB


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