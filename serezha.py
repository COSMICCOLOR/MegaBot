import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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

conn = sqlite3.connect('restaurant1.db', check_same_thread=False)
with conn:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM CategoryDish")
    data = cursor.fetchall()  # fetchone
    column_names = [i[1] for i in conn.execute(f"SELECT * FROM CategoryDish")]
    column_ids = [i[0] for i in conn.execute(f"SELECT * FROM CategoryDish")]
    column_dict = dict(zip(column_names, column_ids))




with conn:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM SubCategory")
    data = cursor.fetchall()  # fetchone
    subcat_names = [i[1] for i in conn.execute(f"SELECT * FROM SubCategory")]
    subcat_ids = [i[4] for i in conn.execute(f"SELECT * FROM SubCategory")]
    subcat_dict = dict(zip(subcat_names, subcat_ids))


with conn:
    data = conn.execute("SELECT * FROM Clients")


with conn:
    data = conn.execute("SELECT * FROM Dish")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Dish")
    data2 = cursor.fetchall()  # fetchone
    dish_names = [i[1] for i in conn.execute(f"SELECT * FROM Dish")]
    dish_cat_ids = [i[11] for i in conn.execute(f"SELECT * FROM Dish")]
    id_dish = [i[0] for i in conn.execute(f"SELECT * FROM Dish")]
    dish_all_dict=dict(zip(dish_names, [[i[1],i[2], i[3], i[4],i[5], i[6], i[7], i[9], i[0]] for i in conn.execute(f"SELECT * FROM Dish")]))

    dish_dict = dict(zip(dish_names, dish_cat_ids))

    # print(dish_names)


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
        [Category_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in column_dict.items()]
        Category_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Category_inline_keyb)
    if call.data.split(':')[1] == "b1":
        bot.send_message(call.message.chat.id, "Что Вас интересует?", reply_markup=Main_inline_keyb)
    if call.data.split(':')[0] in column_dict:
        Sub_inline_keyb = InlineKeyboardMarkup()
        [Sub_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in subcat_dict.items() if str(value) == call.data.split(':')[1]]
        Sub_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Sub_inline_keyb)
    if call.data.split(':')[0] in subcat_dict:
        Dish_inline_keyb = InlineKeyboardMarkup()
        [Dish_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in dish_dict.items() if str(value) == call.data.split(':')[1]]
        Dish_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Dish_inline_keyb)
        # print(call.data.split(':')[0], call.data.split(':')[1])
    global dish_ids
    global dish_names
    if call.data.split(':')[0] in dish_dict:
        dish_ids = []
        markup_dish = InlineKeyboardMarkup(row_width=5)
        markup_dish.add(InlineKeyboardButton("В корзину", callback_data="0:basket"), InlineKeyboardButton('<', callback_data='1:left'), InlineKeyboardButton('Кол-во', callback_data='None'), InlineKeyboardButton('>', callback_data='2:right'), InlineKeyboardButton('Заказать', callback_data='3:buy'))
        if call.data.split(':')[0] in dish_all_dict:
            # img = open(rf"C:\Users\admin\MegaBot\photo\{dish_all_dict[call.data.split(':')[0]][2]}", 'rb')
            # bot.send_photo(call.message.chat.id, img)
            dish_ids.append(dish_all_dict[call.data.split(':')[0]][8])
            dish_names = dish_all_dict[call.data.split(':')[0]][0]
            bot.send_message(call.message.chat.id,  f"{call.data.split(':')[0]}\nОписание:{dish_all_dict[call.data.split(':')[0]][1]}\nЦена: {dish_all_dict[call.data.split(':')[0]][3]}BYN (В упаковке вы увидите  {dish_all_dict[call.data.split(':')[0]][7]}шт.)\nВес:"
                                                    f" {dish_all_dict[call.data.split(':')[0]][5]}"
                                                    f" {dish_all_dict[call.data.split(':')[0]][6]}\nВремя "
                                                    f"приготовления: {dish_all_dict[call.data.split(':')[0]][4]} миунут!\n", reply_markup = markup_dish)

    global dict_info_dish_id
    client_id = int(call.message.chat.id)
    if call.data.split(':')[1] == 'basket':
        dict_info_dish_id = int(dish_ids[0])
        print(dict_info_dish_id, type(dict_info_dish_id))
        cursor.execute("INSERT OR IGNORE INTO ShoppingCart (client_id, dish_id, total_price) values(?, ?, ?);", (client_id, dict_info_dish_id, 5.0))
    conn.commit()


    if call.data.split(':')[1] == 'buy':
        sravnenie_ids = [i[0] for i in cursor.execute(f'SELECT ShoppingCart.dish_id FROM ShoppingCart WHERE ShoppingCart.client_id = {client_id}')]
        info = []
        for i in sravnenie_ids:
            dish_name_cart = cursor.execute(f'SELECT * FROM Dish WHERE Dish.id = {i}')
            infos = [i for i in dish_name_cart]
            info.append(infos)
        print(info)
        result = ""
        total_price = 0
        for i in info:
            for j in i:
                total_price += j[4]
                result+=f'Блюдо: {j[1]}\n'
        bot.send_message(call.message.chat.id, f'{result} Цена:{total_price}')


print("Ready")
bot.infinity_polling(none_stop=True, interval=0)