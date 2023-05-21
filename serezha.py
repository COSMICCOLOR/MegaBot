


import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import sqlite3

import array
import gspread
import requests
import subprocess
import os
import datetime
import uuid

# logfile = str(datetime.date.today()) + '.log' # формируем имя лог-файла
token = '5991850571:AAGwpP8X-kv-nN0P55SciR2sMxCvLkGOeuU'
bot = telebot.TeleBot(token)


#Создание клавиатуры + кнопок
def  createbutton(markup,list_category):
    markup = markup
    for cortej_category in list_category:
        print(cortej_category[0], cortej_category[1])
        markup.add(InlineKeyboardButton(f'{cortej_category}', callback_data=f"info:{cortej_category}"))
    return markup


conn = sqlite3.connect('restaurant1.db')
with conn:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM CategoryDish")
    data = cursor.fetchall()  # fetchone
    column_names = [i[1] for i in conn.execute(f"SELECT * FROM CategoryDish")]
print(column_names)

with conn:
    data = conn.execute("SELECT * FROM Clients")
    print(data.fetchall())

with conn:
    data = conn.execute("SELECT * FROM Dish")
    print(data.fetchall())

# Создаем клавиатуру и кнопки для главного меню USER-панели
Main_inline_keyb = InlineKeyboardMarkup()
Main_inline_keyb.add(InlineKeyboardButton("Меню ресторана", callback_data="menu:txt1"))
Main_inline_keyb.add(InlineKeyboardButton("Отзывы", callback_data="menu:txt2"))
Main_inline_keyb.add(InlineKeyboardButton("Моя корзина", callback_data="menu:txt3"))
Main_inline_keyb.add(InlineKeyboardButton("Мои заказы", callback_data="menu:txt4"))
Main_inline_keyb.add(InlineKeyboardButton("О нас", callback_data="menu:txt5"))
Main_inline_keyb.add(InlineKeyboardButton("Профиль пользователя", callback_data="menu:txt6"))


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text.lower() == '/start':
        bot.send_message(message.chat.id, '''Добро пожаловать в чат-бот "FoodBot". Здесь Вы можете заказать еду по вкусу из ресторана "Літвіны".\nЧто Вас интересует?''', reply_markup=Main_inline_keyb)

@bot.callback_query_handler(func=lambda call: call.data.split(":"))
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id,)
    if call.data.split(':')[1] == "txt1":
        Category_inline_keyb = InlineKeyboardMarkup()
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=createbutton(Category_inline_keyb,column_names))
    if call.data.split(':')[1] == "b1":
        bot.send_message(call.message.chat.id, "Что Вас интересует?", reply_markup=Main_inline_keyb)

print("Ready")
bot.infinity_polling(none_stop=True, interval=0)
