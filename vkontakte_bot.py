import os
import random
import re

import redis
import vk_api
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from parsing_quiz_file import get_question_and_answer


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)
    return keyboard


def request_new_question(vk, quiz, redis_db, user_id, giveup_solution=False):
    question_text = random.choice(list(quiz.keys()))
    correct_solution = quiz.get(question_text)
    redis_db.set(user_id, correct_solution)
    reply(user_id, vk, question_text, giveup_solution)


def check_answer(quiz, redis_db, user_id, text, vk):
    user_question = redis_db.get(user_id).decode("utf-8")
    correct_solution = quiz.get(user_question)
    user_answer = text.split()
    match = any(re.search(rf"\b{answer}\b", correct_solution, re.IGNORECASE) for answer in user_answer)
    if not match:
        result = 'Неправильно… Попробуешь ещё раз?'
    else:
        result = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    reply(user_id, vk, result)


def reply(user_id, vk, text):
    keyboard = create_keyboard()  # Assuming create_keyboard() is defined elsewhere
    vk.messages.send(
        user_id=user_id,
        message=text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def handle_give_up(vk, quiz, redis_db, user_id):
    answer = redis_db.get(user_id)
    if answer:
        giveup_solution = "Правильный ответ: " + answer.decode('utf-8')
        request_new_question(vk, quiz, redis_db, user_id, giveup_solution)
    else:
        refused_surrendering = 'Вы не можете сдаться, пока не зададите вопрос.'
        reply(user_id, vk, refused_surrendering)


def handle_greeting(user_id, vk):
    greeting_text = "Привет! Я бот для викторин. Нажми кнопку «Новый вопрос», чтобы проверить свои знания."
    reply(user_id, vk, greeting_text)


def listen_vk_events(longpoll, vk, quiz, redis_db):
    command_functions = {
        "Новый вопрос": lambda: request_new_question(vk, quiz, redis_db, user_id),
        "Сдаться": lambda: handle_give_up(vk, quiz, redis_db, user_id),
        "Привет": lambda: handle_greeting(user_id, vk)
    }

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text
            user_id = event.user_id
            command_functions.get(text, lambda: check_answer(quiz, redis_db, user_id, text, vk))()


def main():
    env = Env()
    env.read_env()

    vk_token = os.environ['VK_TOKEN']
    quiz_file = os.environ['QUIZ_FILE']
    redis_host = os.environ['HOST']
    redis_port = os.environ['PORT']
    redis_password = os.environ['PASSWORD']

    quiz = get_question_and_answer(quiz_file)
    redis_db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password)

    vk_session = vk_api.VkApi(token=vk_token)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    listen_vk_events(longpoll, vk, quiz, redis_db)


if __name__ == '__main__':
    main()
