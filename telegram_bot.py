import os
import random
import re
from functools import partial

import redis
from environs import Env
from telegram import Bot, Update
from telegram.ext import (
    CommandHandler, ConversationHandler, Filters, MessageHandler, Updater,
)

from quizbot import handlers, static_text
from quizbot.keyboard_utils import make_keyboard_for_start_command

env = Env()
env.read_env()

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
QUIZ_FILE = os.environ['QUIZ_FILE']
REDIS_HOST = os.environ['HOST']
REDIS_PORT = os.environ['PORT']
REDIS_PASSWORD = os.environ['PASSWORD']


def command_start(update: Update, context):
    user_info = update.message.from_user.to_dict()
    text = static_text.start_created.format(
        first_name=user_info['first_name']
    )
    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_start_command(),

    )
    return handlers.NEW_QUESTION


def get_question_and_answer():
    with open(QUIZ_FILE, 'r', encoding='KOI8-R') as quiz_file:
        text = quiz_file.read()
    questions = re.findall(r'Вопрос \d+:\s(\D+)\s\sОтвет:', text)
    answers = re.findall(r'Ответ:\s(.+)\s\s', text)
    questions_and_answers_dict = dict(zip(questions, answers))
    return questions_and_answers_dict


def get_new_question(quiz: dict, redis_db, update: Update, context):
    question_text = random.choice(list(quiz.keys()))
    context.user_data['solution'] = quiz.get(question_text)
    redis_db.set(update.message.chat_id, question_text)
    update.message.reply_text(question_text)
    return handlers.ANSWER


def check_answer(quiz, redis_db, update: Update, context):
    user_id = update.message.chat.id
    answer = update.message.text
    user_question = redis_db.get(user_id)
    correct_solution = quiz.get(user_question)
    user_answer = answer.split()
    match = any(re.search(rf"\b{answer}\b", correct_solution, re.IGNORECASE) for answer in user_answer)
    if match is False:
        result = 'Неправильно… Попробуешь ещё раз?'
    else:
        result = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'

    update.message.reply_text(result, reply_markup=make_keyboard_for_start_command())


def give_up(quiz, redis_db, update: Update, context):
    update.message.reply_text(f'Правильный ответ: {context.user_data["solution"]}\nСледующий вопрос:')
    get_new_question(quiz, redis_db, update, context)


def quiz_score(update: Update, context):
    pass


def main() -> None:
    quiz = get_question_and_answer()
    redis_db = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD)
    quiz_handler = ConversationHandler(
        entry_points=[CommandHandler('start', command_start)],
        states={
            handlers.NEW_QUESTION: [
                MessageHandler(Filters.regex('^(Новый вопрос)$'),
                               partial(get_new_question, quiz, redis_db)),
            ],
            handlers.ANSWER: [
                MessageHandler(
                    Filters.text & ~Filters.regex('Новый вопрос') & ~Filters.regex('Сдаться') & ~Filters.command,
                    partial(check_answer, quiz, redis_db)),
                MessageHandler(Filters.regex('Новый вопрос'),
                               partial(get_new_question, quiz, redis_db)),
                MessageHandler(
                    Filters.regex('Сдаться'),
                    partial(give_up, quiz, redis_db)),
            ],
            handlers.SCORE: [
                MessageHandler(Filters.regex('^(Мой счёт)$'), quiz_score)
            ]
        },
        fallbacks=[]
    )
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(quiz_handler)
    dp.add_handler(CommandHandler("start", command_start))

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f'https://t.me/{bot_info["username"]}'

    print(f"Pooling of '{bot_link}' started")

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
