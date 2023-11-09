import re


def get_question_and_answer(QUIZ_FILE):
    with open(QUIZ_FILE, 'r', encoding='KOI8-R') as quiz_file:
        text = quiz_file.read()
    questions = re.findall(r'Вопрос \d+:\s(\D+)\s\sОтвет:', text)
    answers = re.findall(r'Ответ:\s(.+)\s\s', text)
    questions_and_answers_dict = dict(zip(questions, answers))
    return questions_and_answers_dict
