```
# Telegram Quiz Bot

Telegram Quiz Bot - это бот для проведения викторин в мессенджере Telegram.

## Настройка

1. Установите все необходимые библиотеки:

```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` и добавьте в него следующие строки:

```env
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
VK_TOKEN=YOUR_VK_BOT_TOKEN
QUIZ_FILE=PATH_TO_QUIZ_FILE
HOST=YOUR_REDIS_SERVER_HOST
PORT=YOUR_REDIS_SERVER_PORT
PASSWORD=YOUR_REDIS_SERVER_PASSWORD
```

Где YOUR_TELEGRAM_BOT_TOKEN - токен вашего бота в Telegram, который вы получите от BotFather, 
YOUR_VK_BOT_TOKEN - токен вашего бота в VK, который вы получите после создания бота в VK, 
PATH_TO_QUIZ_FILE - путь к файлу с вопросами и ответами для викторины, 
YOUR_REDIS_SERVER_HOST - адрес вашего Redis-сервера, 
YOUR_REDIS_SERVER_PORT - порт вашего Redis-сервера, 
YOUR_REDIS_SERVER_PASSWORD - пароль вашего Redis-сервера.

3. Создайте файл с вопросами и ответами в формате:

```
Вопрос 1:
Ваш вопрос

Ответ:
Ваш ответ

Вопрос 2:
Ваш вопрос

Ответ:
Ваш ответ
```

4. Запустите Telegram бота:

```bash
python telegram_bot.py
```

5. Запустите VK бота:

```bash
python vkontakte_bot.py
```

## Использование

После запуска бота вам будет доступна команда `/start`, которая запускает викторину. 
Далее, вы сможете выбрать "Новый вопрос", чтобы получить вопрос для ответа, 
"Сдаться", чтобы получить правильный ответ на текущий вопрос, и "Мой счет", чтобы узнать ваш текущий счет в викторине.
```