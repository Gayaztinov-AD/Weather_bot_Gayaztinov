import telebot
import requests
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)

token = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(token)
api_url = 'https://stepik.akentev.com/api/weather'

import re
from datetime import datetime

states = {}
MAIN = 'main'
ANSWER = 'answer'
DAY = 'day'

@bot.message_handler(func=lambda message: True)
def dispatcher(message):
    print(states)
    user_id = message.from_user.id
    state=states.get(user_id, MAIN)
    print('current user', user_id, state)
    print(message.text)
    if state == MAIN:
        main_handler(message)
    elif state == ANSWER:
        weather_answer(message)
    elif state == DAY:
        weather_day(message)

def main_handler(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Это бот-погода. Поможет узнать погоду в любом городе. Какой город интересует?')
        states[message.from_user.id] = ANSWER

def weather_answer(message):
    if message.text == 'Москва':
        res = requests.get(api_url, params={'city': message.text}, verify=False).json()
        bot.send_message(message.from_user.id, 'Сейчас ' + str(res['temp']))
        states[message.from_user.id] = MAIN
    elif message.text == 'Москва завтра':
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(
            *[KeyboardButton(button) for button in ['сегодня', 'завтра', 'послезавтра', 'послепослезавтра']]
        )
        bot.send_message(message.from_user.id, 'Точно на завтра? Введи сегодня, завтра, послезавтра или послепослезавтра!', reply_markup=markup)
        states[message.from_user.id] = DAY

    elif message.text == 'Москва 30.05':
        result = re.search("(.+)\s(\d{2}).(\d{2})", message.text)
        groups = result.groups()
        first_digit = groups[0]
        second_digit = groups[1]
        third_digit = groups[2]
        date = datetime(year=int(datetime.now().year), month=int(third_digit), day=int(second_digit))
        now = datetime.now()
        X = now - date
        X = int(X.days)
        if X in range(0, 4):
            res = requests.get(api_url, params={'city': first_digit, 'forecast': X}, verify=False).json()
            bot.send_message(message.from_user.id, second_digit + '.' + third_digit + ' ' + str(res['temp']))
            states[message.from_user.id] = MAIN
    else:
         bot.reply_to(message, 'Я тебя не понял')
         states[message.from_user.id] = MAIN

def weather_day(message):
    if message.text == 'сегодня':
        res = requests.get(api_url, params={'city': 'Москва', 'forecast': 0}, verify=False).json()
        bot.send_message(message.from_user.id, 'Сегодня ' + str(res['temp']))
        states[message.from_user.id] = MAIN
    elif message.text == 'завтра':
        res = requests.get(api_url, params={'city': 'Москва', 'forecast': 1}, verify=False).json()
        bot.send_message(message.from_user.id, 'Завтра ' + str(res['temp']))
        states[message.from_user.id] = MAIN
    elif message.text == 'послезавтра':
        res = requests.get(api_url, params={'city': 'Москва', 'forecast': 2}, verify=False).json()
        bot.send_message(message.from_user.id, 'послезавтра ' + str(res['temp']))
        states[message.from_user.id] = MAIN
    elif message.text == 'послепослезавтра':
        res = requests.get(api_url, params={'city': 'Москва', 'forecast': 3}, verify=False).json()
        bot.send_message(message.from_user.id, 'послепослезавтра ' + str(res['temp']))
        states[message.from_user.id] = MAIN

bot.polling()