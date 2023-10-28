import json
import os
import random
import re

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from redis_connection import HOST, PASSWORD, PORT, connection

VK_TOKEN = os.environ['VK_TOKEN']
QUIZ_FILE = os.environ['QUIZ_FILE']


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)
    return keyboard


keyboard = create_keyboard()


def new_question_request(vk, quiz, redis_db, user_id, giveup_solution=False):
    question_text = random.choice(list(quiz.keys()))
    correct_solution = quiz.get(question_text)
    redis_db.set(user_id, correct_solution)
    reply(user_id, vk, question_text, giveup_solution)
    return question_text, correct_solution


def check_answer(quiz, redis_db, user_id, text, vk):
    user_question = redis_db.get(user_id).decode("utf-8")
    correct_solution = quiz.get(user_question)
    user_answer = text.split()
    match = any(re.search(rf"\b{answer}\b", correct_solution, re.IGNORECASE) for answer in user_answer)
    if match is False:
        result = 'Неправильно… Попробуешь ещё раз?'
    else:
        result = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    reply(user_id, vk, result)


def reply(user_id, vk, text, correct_solution=False):
    vk.messages.send(user_id=user_id,
                     message=(correct_solution + '\n\n' + text) if correct_solution else text,
                     keyboard=keyboard.get_keyboard(),
                     random_id=random.randint(1, 1000))


def vk_events(longpoll, vk, quiz, redis_db):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text
            user_id = event.user_id
            if text == "Новый вопрос":
                question_text, correct_solution = new_question_request(vk, quiz, redis_db, user_id)
            elif text == "Сдаться":
                try:
                    giveup_solution = "Правильный ответ: " + redis_db.get(user_id).decode('utf-8')
                    question_text, correct_solution = new_question_request(vk, quiz, redis_db, user_id,
                                                                           giveup_solution)
                except UnboundLocalError:
                    refused_surrendering = 'Вы не можете сдаться, пока не зададите вопрос.'
                    reply(user_id, vk, refused_surrendering)
            elif text == "Привет":
                greeting_text = "Привет! Я бот для викторин. Нажми кнопку «Новый вопрос», чтобы проверить свои знания."
                reply(user_id, vk, greeting_text)
            else:
                check_answer(quiz, redis_db, user_id, text, vk)


def main():
    while True:
        with open(QUIZ_FILE, "r", encoding='utf-8') as quiz_file:
            quiz = json.load(quiz_file)

        redis_db = connection(PORT, HOST, PASSWORD)

        vk_session = vk_api.VkApi(token=VK_TOKEN)
        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()

        vk_events(longpoll, vk, quiz, redis_db)


if __name__ == '__main__':
    main()
