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
token = '6112420224:AAFd0gDtUiAC2qqWo4osq82D6qyGH07c_UY'
bot = telebot.TeleBot(token)

conn = sqlite3.connect('restaurant1.db')
with conn:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM CategoryDish")
    data = cursor.fetchall()  # fetchone
    column_names = [i[1] for i in conn.execute(f"SELECT * FROM CategoryDish")]
    column_ids = [i[0] for i in conn.execute(f"SELECT * FROM CategoryDish")]
    column_dict = dict(zip(column_names, column_ids))
# print(column_names)
# print(column_ids)
# print(column_dict)


with conn:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM SubCategory")
    data = cursor.fetchall()  # fetchone
    subcat_names = [i[1] for i in conn.execute(f"SELECT * FROM SubCategory")]
    cat_ids = [str(i[4]) for i in conn.execute(f"SELECT * FROM SubCategory")]
    subcat_id = [str(i[0]) for i in conn.execute(f"SELECT * FROM SubCategory")]
    subcat_dict = dict(zip(subcat_names, cat_ids))  # словарь {название субкатегории: id CategoryDish}
    subcat_dict2 = dict(zip(subcat_names, subcat_id))  # словарь {название субкатегории: id SubCategory}
    subcat_dict3 = {k: ''.join([d[k] for d in (subcat_dict, subcat_dict2)]) for k in subcat_dict.keys()}  # словарь {название субкатегории: 'id CategoryDish+id SubCategory'} значение из двух айдишек будем потом разбивать в колбэк дате
# print(subcat_names)
# print(cat_ids)
# print(subcat_dict)
# print(subcat_dict3)

with conn:
    data = conn.execute("SELECT * FROM Clients")
    # print(data.fetchall())

with conn:
    data = conn.execute("SELECT * FROM Dish")
    print(data.fetchall())
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Dish")
    data2 = cursor.fetchall()  # fetchone
    dish_names = [i[1] for i in conn.execute(f"SELECT * FROM Dish")]
    dish_cat_ids = [i[11] for i in conn.execute(f"SELECT * FROM Dish")]
    dish_dict = dict(zip(dish_names, dish_cat_ids))
    dish_all_dict=dict(zip(dish_names, [[i[1],i[2], i[3], i[4],i[5], i[6], i[7], i[9]] for i in conn.execute(f"SELECT * FROM Dish")]))

# print(dish_names)
# print(dish_dict)

with conn:
    data = conn.execute("SELECT * FROM Reviews")
    print(data.fetchall())
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Reviews")
    data_feedback = cursor.fetchall()  # fetchone
    feedback = [i[1] for i in conn.execute(f"SELECT * FROM Reviews")]
    cursor.execute("SELECT * FROM Clients WHERE id = 4")
    gg = cursor.fetchall()
    print(gg)

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
        print("главные категории")
        # Создаем клавиатуру и кнопки для главного меню ресторана (напр., "Японская кухня")
        global Category_inline_keyb
        Category_inline_keyb = InlineKeyboardMarkup()
        [Category_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in column_dict.items()]
        Category_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Category_inline_keyb)
    if call.data.split(':')[1] == "b1":
        bot.send_message(call.message.chat.id, "Что Вас интересует?", reply_markup=Main_inline_keyb)
    if call.data.split(':')[1] == "b2":
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Category_inline_keyb)
    if call.data.split(':')[0] in column_dict:
        print("субкатегории")
        print(call.data.split(':')[0], call.data.split(':')[1])
        # Создаем клавиатуру и кнопки для субкатегорий (напр., "Суши и роллы")
        global Sub_inline_keyb
        Sub_inline_keyb = InlineKeyboardMarkup()
        [Sub_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in subcat_dict3.items() if str(value[0]) == call.data.split(':')[1]]
        Sub_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        Sub_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:b2"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Sub_inline_keyb)
    if call.data.split(':')[0] in subcat_dict3:
        print("виды однородных блюд типа супы, пиццы и тд")
        print(call.data.split(':')[0], call.data.split(':')[1][1])
        # Создаем клавиатуру и кнопки для конкретных блюд внутри субкатегорий (напр., "Филадельфия маки")
        Dish_inline_keyb = InlineKeyboardMarkup()
        [Dish_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in dish_dict.items() if str(value) == call.data.split(':')[1][1]]
        Dish_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        Dish_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:b3"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Dish_inline_keyb)

    if call.data.split(':')[0] in dish_dict:
        print(call.data.split(':')[0])
        markup_dish = InlineKeyboardMarkup(row_width=3)
        markup_dish.add(InlineKeyboardButton('<', callback_data='left'),
                        InlineKeyboardButton('Кол-во', callback_data='None'),
                        InlineKeyboardButton('>', callback_data='right'),
                        InlineKeyboardButton('Заказать', callback_data='buy'),
                        InlineKeyboardButton("В корзину", callback_data="basket"),)
        if call.data.split(':')[0] in dish_all_dict:
            # img = open(rf"C:\Users\admin\MegaBot\photo\{dish_all_dict[call.data.split(':')[0]][2]}", 'rb')
            # bot.send_photo(call.message.chat.id, img)
            bot.send_message(call.message.chat.id,
                             f"{call.data.split(':')[0]}\nОписание:{dish_all_dict[call.data.split(':')[0]][1]}\nЦена: {dish_all_dict[call.data.split(':')[0]][3]}BYN (В упаковке вы увидите  {dish_all_dict[call.data.split(':')[0]][7]}шт.)\nВес:"
                             f" {dish_all_dict[call.data.split(':')[0]][5]}"
                             f" {dish_all_dict[call.data.split(':')[0]][6]}\nВремя "
                             f"приготовления: {dish_all_dict[call.data.split(':')[0]][4]} миунут!\n",
                             reply_markup=markup_dish)

    if call.data.split(':')[1] == "b3":
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Sub_inline_keyb)
    if call.data.split(':')[1] == "txt2":
        Reviews_inline_keyb = InlineKeyboardMarkup()
        Reviews_inline_keyb.add(InlineKeyboardButton("Наш сервис (отзывы)", callback_data="review:r1"))
        Reviews_inline_keyb.add(InlineKeyboardButton("Наша еда (отзывы)", callback_data="review:r2"))
        Reviews_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        bot.send_message(call.message.chat.id, "Выбирайте:", reply_markup=Reviews_inline_keyb)
        bot.send_message(call.message.chat.id, f"{gg}")





print("Ready")
bot.infinity_polling(none_stop=True, interval=0)
