import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import sqlite3
import os
import array, gspread, requests, subprocess, datetime, uuid
import datetime as DT
import time
import json


# logfile = str(datetime.date.today()) + '.log' # формируем имя лог-файла
token = '6112420224:AAFd0gDtUiAC2qqWo4osq82D6qyGH07c_UY'
bot = telebot.TeleBot(token)
PHOTO_DIR = 'photo'
conn = sqlite3.connect('DATABASE/restaurant1.db', check_same_thread=False)
markdown = """
    *bold text*
    _italic text_
    [text](URL)
    """

clients_json_id = []
message_dict_id = {}

global dish_dict
try:
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM CategoryDish")
        data = cursor.fetchall()  # fetchone
        column_names = [i[1] for i in conn.execute(f"SELECT * FROM CategoryDish")]
        column_ids = [i[0] for i in conn.execute(f"SELECT * FROM CategoryDish")]
        column_dict = dict(zip(column_names, column_ids))
except Exception as e:
    print(e)

try:
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
except Exception as e:
    print(e)

try:
    with conn:
        global client_id
        clients_telegram_id = [i[4] for i in conn.execute(f"SELECT * FROM Clients")]
        print("айди телеги юзеров", clients_telegram_id)
except Exception as e:
    print(e)

try:
    with conn:
        orders_telegram_id = [i[5] for i in conn.execute(f"SELECT * FROM Orders")]  # telegram id юзеров, сделавших заказ
        orders_datetime = [i[4] for i in conn.execute(f"SELECT * FROM Orders")]
        print(type(orders_telegram_id[0]), orders_telegram_id)
except Exception as e:
    print(e)

try:
    with conn:
        # data = conn.execute("SELECT * FROM Dish")
        # print(data.fetchall())
        # cursor = conn.cursor()
        # cursor.execute(f"SELECT * FROM Dish")
        # data2 = cursor.fetchall()  # fetchone
        dish_names = [i[1] for i in conn.execute(f"SELECT * FROM Dish WHERE is_stop = 'В продаже'")]
        dish_cat_ids = [str(i[11]) for i in conn.execute(f"SELECT * FROM Dish WHERE is_stop = 'В продаже'")]
        dish_ids = [str(i[0]) for i in conn.execute(f"SELECT * FROM Dish")]
        dish_status = [i[8] for i in conn.execute(f"SELECT * FROM Dish")]
        dish_dict2 = dict(zip(dish_names, dish_ids))
        dish_dict = dict(zip(dish_names, dish_cat_ids))
        dish_all_dict = dict(zip(dish_names, [[i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[9], i[0]] for i in conn.execute(f"SELECT * FROM Dish")]))
except Exception as e:
    print(e)

try:
    with conn:
        data = conn.execute("SELECT * FROM Reviews")
        print(data.fetchall())
        review_order = [i[1] for i in conn.execute(f"SELECT * FROM Reviews WHERE accept = 'YES'")]
        review_dish = [i[2] for i in conn.execute(f"SELECT * FROM Reviews")]
        client_id = [i[3] for i in conn.execute(f"SELECT * FROM Reviews WHERE accept = 'YES'")]
        orders_id = [i[4] for i in conn.execute(f"SELECT * FROM Reviews")]
        review_id = [i[0] for i in conn.execute(f"SELECT * FROM Reviews")]
        print("qqqqqqqqq", review_order, client_id)
        dish_id = [str(i[5]) for i in conn.execute(f"SELECT * FROM Reviews")]
        review_order_dict = dict(zip(review_order, client_id))  # можно корректировать индексами количество выводимых отзывов
        print(review_order_dict)
        review_dish_dict = dict(zip(dish_id, review_dish))
        print(review_dish_dict)
        client_name = [i[1] for i in conn.execute(f"SELECT * FROM Clients")]
        client_id2 = [i[0] for i in conn.execute(f"SELECT * FROM Clients")]
        client_dict = dict(zip(client_id2, client_name))
        print(client_dict)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Reviews")
        data_feedback = cursor.fetchall()  # fetchone
        feedback = [i[1] for i in conn.execute(f"SELECT * FROM Reviews")]
        cursor.execute("SELECT * FROM Clients WHERE id = 4")
        gg = cursor.fetchall()
        print(gg)
except Exception as e:
    print(e)

# Создаем клавиатуру и кнопки для главного меню USER-панели
Main_inline_keyb = InlineKeyboardMarkup()
Main_inline_keyb.add(InlineKeyboardButton("Меню ресторана", callback_data="menu:txt1"))
Main_inline_keyb.add(InlineKeyboardButton("Моя корзина", callback_data="menu:txt3"))
Main_inline_keyb.add(InlineKeyboardButton("История заказов", callback_data="menu:txt4"))
Main_inline_keyb.add(InlineKeyboardButton("О нас", callback_data="menu:txt2"))
Main_inline_keyb.add(InlineKeyboardButton("Профиль пользователя", callback_data="menu:profile"))

# Создаем клавиатуру и кнопки для ADMIN-панели 1 уровня доступа
Admin_keyb_lvl1 = InlineKeyboardMarkup()
Admin_keyb_lvl1.add(InlineKeyboardButton("Добавить администратора➕", callback_data="admin_lvl1:addadmin"))
Admin_keyb_lvl1.add(InlineKeyboardButton("Удалить администратора➖", callback_data="admin_lvl1:deladmin"))
Admin_keyb_lvl1.add(InlineKeyboardButton("Редактировать профиль администратора🛠️", callback_data="admin_lvl1:redadmin"))

# Создаем клавиатуру и кнопки для ADMIN-панели 2 уровня доступа
Admin_keyb_lvl2 = InlineKeyboardMarkup()
Admin_keyb_lvl2.add(InlineKeyboardButton("Утвердить отзывы о заказах", callback_data="admin_lvl2:admin_orders_rev"))
Admin_keyb_lvl2.add(InlineKeyboardButton("Утвердить отзывы о блюдах", callback_data="admin_lvl2:admin_dishes_rev"))
Admin_keyb_lvl2.add(InlineKeyboardButton("Добавить блюдо", callback_data="admin_lvl2:admin_dish_add"))
Admin_keyb_lvl2.add(InlineKeyboardButton("Блюдо на СТОП", callback_data="admin_lvl2:admin_dish_stop"))

global msg_to_admin
msg_to_admin = 'Поступил заказ'
markup_administration = InlineKeyboardMarkup()
markup_administration.add(InlineKeyboardButton(msg_to_admin, callback_data='0:order_is_ready'))


"""***START Функция для создания клавиатуры с обновляемой кнопкой количества заказываемого блюда START***"""
count = 1  # переменная для хранения количества добавляемого в корзину блюда
def create_keyboard(dish_id):  # функция для создания клавиатуры под карточкой блюда
    markup_dish = InlineKeyboardMarkup(row_width=3)
    markup_dish.add(InlineKeyboardButton('-', callback_data='dish_card:minus'),
                    InlineKeyboardButton(str(count), callback_data=':count'),
                    InlineKeyboardButton('+', callback_data='dish_card:plus'),
                    InlineKeyboardButton("В корзину", callback_data="dish_card:basket"),
                    InlineKeyboardButton('Отзывы', callback_data=f'dish_card:dish_feedback:{dish_id}'))
    return markup_dish
"""***END Функция для создания клавиатуры с обновляемой кнопкой количества заказываемого блюда END***"""


"""***START Функция для создания клавиатуры для изменения профиля пользователя START***"""
profile_edit_data = {"Изменить имя": "edit:name",
                     "Изменить телефон": "edit:phone_number",
                     "Изменить адрес": "edit:delivery_adress",
                     "Вернуться в меню": "menu:b1"}
def create_edit_button(dct):  # функция для создания кнопок для изменения полей профиля пользователя, принимает словарь
    edit_button = telebot.types.InlineKeyboardMarkup()
    for key, value in dct.items():
        edit_button.add(telebot.types.InlineKeyboardButton(key, callback_data=value))
    return edit_button
"""***END Функция для создания клавиатуры для изменения профиля пользователя END***"""


global field, field_dict
field_dict = {"name": "Имя", "phone_number": "Телефон", "delivery_adress": "Адрес"}
field = 'name'
global reg_name, reg_phone_number, reg_delivery_adress  # значения (данные юзера) при регистрации по умолчанию, к-е будем потом изменять
reg_name, reg_phone_number, reg_delivery_adress = "Указать имя", "Указать телефон", "Указать адрес"
global reg_field, reg_field_dict
reg_field = "name"  # получаем название поля для изменения
reg_field_dict = {"name": "Имя", "phone_number": "Телефон", "delivery_adress": "Адрес"}
def create_registration_keyb():  # функция для создания кнопок для регистрации пользователя
    registration_keyb = telebot.types.InlineKeyboardMarkup(row_width=1)
    registration_keyb.add(InlineKeyboardButton(reg_name, callback_data="reg:name"),
                          InlineKeyboardButton(reg_phone_number, callback_data="reg:phone_number"),
                          InlineKeyboardButton(reg_delivery_adress, callback_data="reg:delivery_adress"),
                          InlineKeyboardButton("Сохранить\u2705", callback_data="accept:save_all"),
                          InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
    return registration_keyb


def create_edit_cart_keyb(dct):  # функция для создания клавиатуры для редактирования корзины, принимает словарь
    Clear_basket_keyb = InlineKeyboardMarkup(row_width=3)
    num = 1
    for key, value in dct.items():
        Clear_basket_keyb.add(InlineKeyboardButton(f"{num}. {key}: {value[1]} шт.", callback_data=f"show:{key}:{value[0]}:{value[1]}"))
        num += 1
        Clear_basket_keyb.add(InlineKeyboardButton("-", callback_data=f"dish-:-:{key}:{value[0]}:{value[1]}"),
                              InlineKeyboardButton("+", callback_data=f"dish+:+:{key}:{value[0]}:{value[1]}"),
                              InlineKeyboardButton("Удалить", callback_data=f"clear_cart:clear_one_dish:{key}:{value[0]}:{value[1]}"))
    Clear_basket_keyb.add(InlineKeyboardButton("Удалить всё из корзины", callback_data="user_basket:clear_basket_all"))
    Clear_basket_keyb.add(InlineKeyboardButton("Показать корзину", callback_data="menu:txt3"))
    Clear_basket_keyb.add(InlineKeyboardButton("Меню", callback_data="menu:b1"))
    return Clear_basket_keyb


def create_admin_review_keyb(dct):  # функция для создания клавиатуры для утверждения отзывов о заказах, принимает словарь
    AdminReviewOrder_inline_keyb = InlineKeyboardMarkup(row_width=4)
    AdminReviewOrder_inline_keyb.add(InlineKeyboardButton("Номер", callback_data="qwerty:qwerty"),
                                     InlineKeyboardButton("Статус", callback_data="qwerty:qwerty"),
                                     InlineKeyboardButton("Утвердить", callback_data="qwerty:qwerty"),
                                     InlineKeyboardButton("Отклонить", callback_data="qwerty:qwerty"))  # неактивные кнопки с фиктивным колбэком
    for key, value in dct.items():
        with conn:
            current_review_status = [i[6] for i in conn.execute(f"SELECT * FROM Reviews WHERE id = {key}")][0]
            print(current_review_status)
        AdminReviewOrder_inline_keyb.add(InlineKeyboardButton(f"{key}.", callback_data=f"edit_review:review_{key}"),
                                         InlineKeyboardButton(f"{value[2]}", callback_data="qwerty:qwerty"),
                                         InlineKeyboardButton("\u2705", callback_data=f"+edit_review:+{key}"),
                                         InlineKeyboardButton("\u274C", callback_data=f"-edit_review:-{key}"))
    AdminReviewOrder_inline_keyb.add(InlineKeyboardButton("Меню", callback_data="menu:b1"))
    AdminReviewOrder_inline_keyb.add(InlineKeyboardButton("Админка", callback_data="admin_lvl2:admin_panel"))
    return AdminReviewOrder_inline_keyb


def create_admin_reviewdish_keyb(dct):  # функция для создания клавиатуры для утверждения отзывов о блюдах, принимает словарь
    AdminReviewDish_inline_keyb = InlineKeyboardMarkup(row_width=4)
    AdminReviewDish_inline_keyb.add(InlineKeyboardButton("Номер", callback_data="qwerty:qwerty"),
                                     InlineKeyboardButton("Статус", callback_data="qwerty:qwerty"),
                                     InlineKeyboardButton("Утвердить", callback_data="qwerty:qwerty"),
                                     InlineKeyboardButton("Отклонить", callback_data="qwerty:qwerty"))  # неактивные кнопки с фиктивным колбэком
    for key, value in dct.items():
        with conn:
            current_reviewdish_status = [i[4] for i in conn.execute(f"SELECT * FROM ReviewDish WHERE id = {key}")][0]
            print(current_reviewdish_status)
        AdminReviewDish_inline_keyb.add(InlineKeyboardButton(f"{key}.", callback_data=f"edit_review_dish:reviewdish_{key}"),
                                         InlineKeyboardButton(f"{value[2]}", callback_data="qwerty:qwerty"),
                                         InlineKeyboardButton("\u2705", callback_data=f"+edit_reviewdish:++{key}"),
                                         InlineKeyboardButton("\u274C", callback_data=f"-edit_reviewdish:--{key}"))
    AdminReviewDish_inline_keyb.add(InlineKeyboardButton("Меню", callback_data="menu:b1"))
    AdminReviewDish_inline_keyb.add(InlineKeyboardButton("Админка", callback_data="admin_lvl2:admin_panel"))
    return AdminReviewDish_inline_keyb


global default_dict_add_dish
default_dict_add_dish = {1: ["Добавить название", "Название", "Напишите название блюда"],
                         2: ["Добавить описание", "Описание", "Добавьте описание блюда"],
                         3: ["Указать стоимость", "0.0", "Укажите стоимость блюда"],
                         4: ["Время готовки, мин.", "0", "Укажите время приготовления блюда в минутах"],
                         5: ["Указать вес/объём", "0.0", "Укажите вес/объём блюда в гр./мл."],
                         6: ["В наличии шт.", "0", "Укажите количество порций блюда в наличии"],
                         7: ["Выбрать меру", "гр./мл.", "Выберите меру измерения блюда"],
                         8: ["Выбрать категорию", "Категория", "Выберите категорию блюда"],
                         9: ["Выбрать субкатегорию", "Субкатегория", "Выберите субкатегорию блюда"],
                         10: ["Добавить фото", "ФОТО", "Пришлите фотографию блюда"]}
def create_admin_adddish_keyb(dct):  # функция для создания клавиатуры для добавления блюда в БД, принимает словарь
    AdminAddDish_inline_keyb = InlineKeyboardMarkup(row_width=2)
    AdminAddDish_inline_keyb.add(InlineKeyboardButton("Выбрать:", callback_data="qwerty:qwerty"),
                                 InlineKeyboardButton("Результат:", callback_data="qwerty:qwerty"))  # неактивные кнопки с фиктивным колбэком
    for key, value in dct.items():
        AdminAddDish_inline_keyb.add(InlineKeyboardButton(f"{key}. {value[0]}", callback_data=f"admin_add_new_dish:add_dish_{key}"),
                                     InlineKeyboardButton(f"{value[1]}", callback_data="qwerty:qwerty"))
    AdminAddDish_inline_keyb.add(InlineKeyboardButton("Сохранить", callback_data="admin_add_dish:save_new_dish"))
    AdminAddDish_inline_keyb.add(InlineKeyboardButton("Админка", callback_data="admin_lvl2:admin_panel"))
    AdminAddDish_inline_keyb.add(InlineKeyboardButton("Меню", callback_data="menu:b1"))
    return AdminAddDish_inline_keyb


def create_admin_stop_dish_keyboard(dct):  # функция для создания клавиатуры для STOP блюда в БД, принимает словарь
    AdminDelDish_inline_keyb = InlineKeyboardMarkup(row_width=2)
    # AdminDelDish_inline_keyb.add(InlineKeyboardButton("Блюдо:                       Статус:", callback_data="qwerty:qwerty"))  # неактивные кнопки с фиктивным колбэком
    for key, value in dct.items():
        # with conn:
            # stop_status = [i[8] for i in conn.execute(f"SELECT * FROM Dish WHERE id = {value}")][0]
            # print(stop_status)
        AdminDelDish_inline_keyb.add(InlineKeyboardButton(f"{key}. {value[0]}: {value[1]}", callback_data=f"qwerty:qwerty"))
        AdminDelDish_inline_keyb.add(InlineKeyboardButton("Изменить\u2705", callback_data=f"stop_dish:{value[1]}:{key}"))
    AdminDelDish_inline_keyb.add(InlineKeyboardButton("Меню", callback_data="menu:b1"))
    AdminDelDish_inline_keyb.add(InlineKeyboardButton("Админка", callback_data="admin_lvl2:admin_panel"))
    return AdminDelDish_inline_keyb


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '''Добро пожаловать в чат-бот "FoodBot". Здесь Вы можете заказать еду по вкусу из ресторана "Літвіны".\nЧто Вас интересует?''', reply_markup=Main_inline_keyb)
    global user_telegram_id
    user_telegram_id = message.from_user.id
    # print(type(user_telegram_id), message.from_user.id)


@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    user_id = message.from_user.id  # id телеги пользователя
    with conn:
        row = [i[1] for i in conn.execute("SELECT * FROM BotAdmins WHERE position = 'admin lvl1'")]
    if user_id not in row:  # проверяем id на пригодность
        bot.send_message(message.chat.id, "Ошибка.\nНет правд доступа.", reply_markup=Main_inline_keyb)
    else:  # если есть, то показываем админу клаву для управления админкой
        bot.send_message(message.chat.id,
                         "Админ-панель 1 уровня.\n"
                         "Функционал: добавление, изменение и удаление админов 2 уровня.", reply_markup=Admin_keyb_lvl1)


@bot.message_handler(commands=['admin'])
def admin_management(message):
    admin_id = message.from_user.id  # id телеги админа 2 уровня
    with conn:
        row = [i[1] for i in conn.execute("SELECT * FROM BotAdmins WHERE position = 'admin lvl2' OR position = 'admin lvl1'")]
    if admin_id not in row:  # проверяем id
        bot.send_message(message.chat.id, "Ошибка.\nНет правд доступа.", reply_markup=Main_inline_keyb)
    else:  # если есть, то показываем админу клаву для управления админкой
        bot.send_message(message.chat.id,
                         "Админ-панель 2 уровня.\n"
                         "Функционал:\n"
                         "- Добавление и удаление блюда;\n"
                         "- Постановка блюда на СТОП\n"
                         "- Обработка отзывов.", reply_markup=Admin_keyb_lvl2)


@bot.callback_query_handler(func=lambda call: call.data.split(":"))
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id,)
    if call.data.split(':')[1] == "qwerty":  # неактивные кнопки в админке
        print("qwerty")
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
        print(call.data.split(':')[0], call.data.split(':')[1][1:], call.data.split(':'))
        # Создаем клавиатуру и кнопки для конкретных блюд внутри субкатегорий (напр., "Филадельфия маки")
        Dish_inline_keyb = InlineKeyboardMarkup()
        [Dish_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in dish_dict.items() if value == call.data.split(':')[1][1:]]
        Dish_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        Dish_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:b3"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Dish_inline_keyb)


#START code Serezha + Dima________________________________
    global dish_ids
    global dish_names
    if call.data.split(':')[0] in dish_dict:
        dish_ids = []
    if call.data.split(':')[0] in dish_all_dict:
        print("yyyyyyyyyyyy", call.data.split(':'), dish_all_dict[call.data.split(':')[0]][2])
        global current_dish_id
        current_dish_id = dish_all_dict[call.data.split(':')[0]][8]
        dish_ids.append(dish_all_dict[call.data.split(':')[0]][8])  # айди бюлюда в карточке
        dish_names = dish_all_dict[call.data.split(':')[0]][0]
        global result_dish  # формируем карточку блюда и отправляем юзеру с клавиатурой для заказа и добавления в корзину
        result_dish = f"{call.data.split(':')[0]}\n" \
                      f"Описание: {dish_all_dict[call.data.split(':')[0]][1]}\n" \
                      f"Цена: {dish_all_dict[call.data.split(':')[0]][3]} BYN (1 шт.)\n" \
                      f"Вес: {dish_all_dict[call.data.split(':')[0]][5]} {dish_all_dict[call.data.split(':')[0]][6]}\n" \
                      f"Время приготовления: {dish_all_dict[call.data.split(':')[0]][4]} миунут\n"
        with open("photo/" + dish_all_dict[call.data.split(':')[0]][2], "rb") as img:  # calldata - id блюда и название соотв-й картинки этого блюда
            bot.send_photo(call.message.chat.id, photo=img)
        bot.send_message(call.message.chat.id, f"{result_dish}", reply_markup=create_keyboard(current_dish_id))

    """***START Обработки колбэка от клавиатуры с обновляемой кнопкой количества заказываемого блюда START***"""
    global count  # используем глобальную переменную для количества добавляемого в корзину блюда
    bot.answer_callback_query(call.id)  # подтверждаем нажатие
    if call.data.split(':')[1] == "minus":  # если нажата кнопка "-"
        if count > 1:  # если количество больше одного
            count -= 1  # уменьшаем количество на один
            bot.edit_message_text(f"{result_dish}", call.message.chat.id, call.message.message_id,
                                  reply_markup=create_keyboard(current_dish_id))  # обновляем сообщение с клавиатурой
    elif call.data.split(':')[1] == "plus":  # если нажата кнопка "+"
        count += 1  # увеличиваем количество на один
        bot.edit_message_text(f"{result_dish}", call.message.chat.id, call.message.message_id,
                              reply_markup=create_keyboard(current_dish_id))  # обновляем сообщение с клавиатурой
    """***END Обработки колбэка от клавиатуры с обновляемой кнопкой количества заказываемого блюда END***"""

    global dict_info_dish_id
    client_telegram_id = int(call.message.chat.id)
    if call.data.split(':')[1] in ['basket', 'basket2', "txt3"]:
        if call.data.split(':')[1] == 'basket':
            """Сначала запишем в Корзину БД данные по id telegram независимо от регистрации пользователя в БД в таблице Clients"""
            dict_info_dish_id = int(dish_ids[0])
            price_dish = [i[0] for i in conn.execute(f"SELECT price FROM Dish WHERE id ={dict_info_dish_id}")][0]
            """Необходимо проверить, добавлял ли уже юзер в корзину данное блюдо"""
            cursor.execute(f"SELECT * FROM ShoppingCart WHERE dish_id ={dict_info_dish_id} AND client_id ={client_telegram_id}")
            check_dish_in_cart = cursor.fetchone()
            print("проверка КОРЗИНЫ добавлял ли уже юзер в корзину данное блюдо", check_dish_in_cart)
            if check_dish_in_cart is None:
                print("ОТ НАНА привет")
                cart = "INSERT OR IGNORE INTO ShoppingCart (client_id, dish_id, total_price, count) values(?, ?, ?, ?)"
                total_price_dish = float(count * price_dish)
                with conn:
                    conn.execute(cart, [client_telegram_id, dict_info_dish_id, total_price_dish, count])
                conn.commit()
                count = 1  # сброс количества заказанного блюда в тексте центральной кнопки карточки
            else:
                print("ОТ ЭЛСА привет")
                count_from_cart = count + [i[4] for i in conn.execute(f"SELECT * FROM ShoppingCart WHERE dish_id ={dict_info_dish_id} AND client_id = {client_telegram_id}")][0]
                print("ОТ count_from_cart привет", count_from_cart)
                total_price_dish2 = float((count_from_cart + count) * price_dish)
                print("ОТ total_price_dish2 привет", total_price_dish2)
                with conn:
                    conn.execute(f"UPDATE ShoppingCart SET total_price = ? WHERE dish_id =? AND client_id = ?",
                                 (total_price_dish2, dict_info_dish_id, client_telegram_id))
                    conn.execute(f"UPDATE ShoppingCart SET count = ? WHERE dish_id =? AND client_id = ?",
                                 (count_from_cart, dict_info_dish_id, client_telegram_id))
                conn.commit()
                count = 1  # сброс количества заказанного блюда в тексте центральной кнопки карточки
        else:  #если basket2, то добавлять нет необх-ти, так как уже до этого добавили, и просто выводим далее корзину
            pass
        """Создаем клавиатуру для корзины после добавления в нее первого блюда"""
        order_after_cart_markup = InlineKeyboardMarkup()
        # order_after_cart_markup.add(InlineKeyboardButton("Добавить блюда в корзину", callback_data="menu:b2"))
        # order_after_cart_markup.add(InlineKeyboardButton("Изменить данные профиля \U0001F464", callback_data="edit2:to_profile"))
        order_after_cart_markup.add(InlineKeyboardButton('Оформить заказ \u2705', callback_data='user_basket:Оформить заказ'))
        order_after_cart_markup.add(InlineKeyboardButton('Редактировать корзину \u274C', callback_data='user_basket:clear_basket'))
        order_after_cart_markup.add(InlineKeyboardButton("Меню", callback_data="menu:b1"))
        """Затем проверяем регистрацию пользователя"""
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id  # id телеги пользователя
        cursor.execute("SELECT * FROM Clients WHERE telegram_id = ?", (user_id,))  # проверка рег-ции пользователя в БД
        row = cursor.fetchone()
        if row is None:  # если нет, то просим пользователя ввести свои данные/зарегистрироваться
            Reg_inline_keyb = InlineKeyboardMarkup()
            Reg_inline_keyb.add(InlineKeyboardButton("РЕГИСТРАЦИЯ", callback_data="prereg:pushreg"))
            Reg_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
            bot.send_message(call.message.chat.id, "Чтобы пользоваться чат-ботом, нужно пройти регистрацию.",
                             reply_markup=Reg_inline_keyb)
        else:  # если есть, то показываем пользователю его корзину+клавиатуру
            check_ids = [i[0] for i in cursor.execute(f'SELECT ShoppingCart.dish_id FROM ShoppingCart WHERE ShoppingCart.client_id = {client_telegram_id}')]
            info = []
            for i in check_ids:
                dish_name_cart = cursor.execute(f'SELECT * FROM Dish WHERE Dish.id = {i}')
                infos = [i for i in dish_name_cart]
                info.append(infos)
            print("Привет от ИНФО тут надо нам цена диша", info)
            result = "Вы добавили в корзину:\n\n" \
                     "Блюдо:  |Цена за 1 шт.| Количество|\n"
            total_price = 0
            for i in info:
                for j in i:
                    print(j[0])
                    with conn:
                        count_dish_cart = [i for i in conn.execute(f'SELECT count FROM ShoppingCart WHERE {j[0]} = ShoppingCart.dish_id')][0][0]
                    # print(count_dish_cart)
                    total_price += float(j[4] * count_dish_cart)
                    result += f'{j[1]}:   {j[4]} р.,   {count_dish_cart} шт.\n'
            # если корзина пуста, то выводим соотв-е сообщение, если не пуста, то карточку корзины
            if len(check_ids) == 0:
                bot.send_message(call.message.chat.id, "Ваша корзина ещё пуста. Добавьте блюда в корзину.", reply_markup=Main_inline_keyb)
            else:
                bot.send_message(call.message.chat.id, f'{result}\nОбщая стоимость: {total_price} р.\u2705', reply_markup=order_after_cart_markup)

    if call.data.split(':')[1] == "dish_feedback":
        global dish_id_from_card
        dish_id_from_card = call.data.split(':')[2]
        DishReview_inline_keyb = InlineKeyboardMarkup()
        DishReview_inline_keyb.add(InlineKeyboardButton("Оставить отзыв", callback_data=f"dish_card:dish_feedback2:{dish_id_from_card}"))
        DishReview_inline_keyb.add(InlineKeyboardButton("Меню", callback_data="menu:b1"))
        print("АЙДИ ТЕКУЩЕГО БЛЮДА", dish_id_from_card)
        with conn:
            dish_feedback = [i[1] for i in conn.execute(f"SELECT * FROM ReviewDish WHERE dish_id = {call.data.split(':')[2]} AND accept = 'YES'")]
            cl_id_feedback = [i[2] for i in conn.execute(f"SELECT * FROM ReviewDish WHERE dish_id = {call.data.split(':')[2]} AND accept = 'YES'")]
            # review_order_dict = dict(zip(review_order[-3:], client_id[-3:]))  # можно корректировать индексами количество выводимых отзывов
            feedback_dish_dict = dict(zip(dish_feedback, cl_id_feedback))
            cl_name = [i[1] for i in conn.execute(f"SELECT * FROM Clients")]
            cl_id2 = [i[0] for i in conn.execute(f"SELECT * FROM Clients")]
            cl_dict = dict(zip(cl_id2, cl_name))
        result_feedback_card = ""
        for key, value in feedback_dish_dict.items():
            result_feedback_card += f"\U0001F5E8{cl_dict[value]}: '{key}'\n\n"
        print("СЛОВАРЬ С ОТЗЫВАМИ", result_feedback_card)
        if len(result_feedback_card) != 0:
            bot.send_message(call.message.chat.id, f"{result_feedback_card}", reply_markup=DishReview_inline_keyb)
        else:
            bot.send_message(call.message.chat.id, f"Отзывов еще нет. Вы можете оставить свой, если заказывали такое блюдо.", reply_markup=DishReview_inline_keyb)
    if call.data.split(':')[1] == "dish_feedback2":
        DishReviewError_inline_keyb = InlineKeyboardMarkup()
        DishReviewError_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        DishReviewError_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:b3"))
        # колонка dish_ids - колонка в Orders - строка из корзины с id заказанных блюд + количество шт.
        ids_string = list(filter(lambda x: dish_id_from_card in x, [list(map(lambda x: x.replace(" ", "").split(":")[0], i[0].split(","))) for i in conn.execute(f"SELECT dish_ids FROM Orders WHERE telegram_id = {call.message.chat.id}")]))

        print("JSONSSSSS ids dishes", ids_string)
        if call.message.chat.id in orders_telegram_id and len(ids_string) != 0:
            print("clients id telegram", call.message.chat.id)
            bot.answer_callback_query(call.id)  # подтвердить нажатие
            bot.send_message(call.message.chat.id,
                             "Понравилось ли Вам данное блюдо?",
                             reply_markup=telebot.types.ForceReply())  # спрашиваем пользователя о его отзыве
        else:
            bot.send_message(call.message.chat.id,
                             "Вы ещё не заказывали у нас такое блюдо.",
                             reply_markup=DishReviewError_inline_keyb)  # выдать клаву если пользователь ранее не заказывал блюдо
        """START Removing items from the cart START"""
    if call.data.split(':')[1] == 'clear_basket':
        # все айди блюд конкретного юзера в корзине + их количество
        dish_id_list = [i[0] for i in cursor.execute(f'SELECT dish_id FROM ShoppingCart WHERE client_id = {client_telegram_id}')]
        # кол-во штук для каждого блюда конкретного юзера в корзине
        count_list = [i[0] for i in cursor.execute(f'SELECT count FROM ShoppingCart WHERE client_id = {client_telegram_id}')]
        dish_id_count = dict(zip(dish_id_list, count_list))
        dish_name_list = [[i[0] for i in conn.execute(f'SELECT name FROM Dish WHERE id = {i}')][0] for i in dish_id_list]
        global dish_name_id_count_dict  # {'Флорида маки': (12, 1), 'Вино "PROSEKKO"': (33, 3), 'Тирамису': (25, 2), 'Пиво "Крыніца"': (14, 1)}
        # словарь {название блюда: (айди блюда конкретного юзера в корзине + количество в корзине)}
        # dish_name_id_count_dict = dict(zip(dish_name_list, dish_id_count.items()))  # внутри будет кортеж, не подходит для изменения
        dish_name_id_count_dict = {}  # Создаем пустой словарь
        for i in range(len(dish_name_list)):  # Проходим по элементам списка и получаем ключ и значение из словаря a по индексу i
            key = list(dish_id_count.keys())[i]
            value = list(dish_id_count.values())[i]
            dish_name_id_count_dict[dish_name_list[i]] = [key, value]  # Добавляем в словарь пару ключ-значение, где ключ - элемент из списка b, а значение - список из ключа и значения из словаря
        print(dish_id_list, count_list, dish_id_count, dish_name_list, dish_name_id_count_dict, sep='\n')
        #отправляем пользователю созданную в функции create_edit_cart_keyb(dish_name_id_count_dict) клавиатуру
        bot.send_message(call.message.chat.id, "Здесь Вы можете редактировать количество добавленных в корзину блюд"
                                               " с помощью кнопок + - удалить", reply_markup=create_edit_cart_keyb(dish_name_id_count_dict))
    bot.answer_callback_query(call.id)  # подтверждаем нажатие
    print("HELLO FROM CART", call.data.split(":"))
    if call.data.split(':')[0] == "dish-":  # если нажата кнопка "-" ['dish_minus', '-', 'Нигири Сяке', '14', '1']
         if int(call.data.split(':')[4]) > 0:  # если количество больше 0
             dish_name_id_count_dict[call.data.split(':')[2]][1] = int(call.data.split(':')[4]) - 1  # - количество на один
             price_dish2 = [i[0] for i in conn.execute(f"SELECT price FROM Dish WHERE id ={int(call.data.split(':')[3])}")][0]
             total_price_dish3 = float(dish_name_id_count_dict[call.data.split(':')[2]][1] * price_dish2)
             with conn:
                 conn.execute(f"UPDATE ShoppingCart SET total_price = ? WHERE dish_id =? AND client_id = ?",
                              (total_price_dish3, int(call.data.split(':')[3]), client_telegram_id))
                 conn.execute(f"UPDATE ShoppingCart SET count = ? WHERE dish_id =? AND client_id = ?",
                              (dish_name_id_count_dict[call.data.split(':')[2]][1], int(call.data.split(':')[3]), client_telegram_id))
             conn.commit()
             bot.edit_message_text(f"Здесь Вы можете редактировать количество добавленных в корзину блюд"
                                               " с помощью кнопок +, -, удалить", call.message.chat.id, call.message.message_id,
                                   reply_markup=create_edit_cart_keyb(dish_name_id_count_dict))  # обновляем сообщение с клавиатурой
         msg = bot.send_message(call.message.chat.id, f"Количество блюда {call.data.split(':')[2]} в корзине уменьшено")
         time.sleep(2)
         bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[0] == "dish+":  # если нажата кнопка "+" ['dish_minus', '+', 'Нигири Сяке', '14', '1']
        dish_name_id_count_dict[call.data.split(':')[2]][1] = int(call.data.split(':')[4]) + 1  # + количество на один
        price_dish2 = [i[0] for i in conn.execute(f"SELECT price FROM Dish WHERE id ={int(call.data.split(':')[3])}")][0]
        total_price_dish3 = float(dish_name_id_count_dict[call.data.split(':')[2]][1] * price_dish2)
        with conn:
            conn.execute(f"UPDATE ShoppingCart SET total_price = ? WHERE dish_id =? AND client_id = ?",
                         (total_price_dish3, int(call.data.split(':')[3]), client_telegram_id))
            conn.execute(f"UPDATE ShoppingCart SET count = ? WHERE dish_id =? AND client_id = ?",
                         (dish_name_id_count_dict[call.data.split(':')[2]][1], int(call.data.split(':')[3]), client_telegram_id))
        conn.commit()
        bot.edit_message_text(f"Здесь Вы можете редактировать количество добавленных в корзину блюд"
                                               " с помощью кнопок +, -, удалить", call.message.chat.id, call.message.message_id,
                                   reply_markup=create_edit_cart_keyb(dish_name_id_count_dict))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Количество блюда {call.data.split(':')[2]} в корзине увеличено")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[1] == "clear_one_dish":  # если нажата кнопка "удалить" ['dish_minus', 'удалить', 'Нигири Сяке', '14', '1']
        with conn:
            conn.execute(f"DELETE FROM ShoppingCart WHERE dish_id = {int(call.data.split(':')[3])}")
        conn.commit()
        dish_name_id_count_dict.pop(call.data.split(':')[2], None)
        bot.edit_message_text(f"Здесь Вы можете редактировать количество добавленных в корзину блюд"
                                               " с помощью кнопок +, -, удалить", call.message.chat.id, call.message.message_id,
                              reply_markup=create_edit_cart_keyb(dish_name_id_count_dict))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, "Блюдо удалено из корзины")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[1] == "clear_basket_all":  # удаление из корзины всех данных пользователя по id telegram
        After_clear_basket_keyb = InlineKeyboardMarkup(row_width=2)
        After_clear_basket_keyb.add(InlineKeyboardButton("Показать корзину", callback_data="menu:txt3"),
                                    InlineKeyboardButton("Меню", callback_data="menu:b1"))
        with conn:
            conn.execute(f'DELETE FROM ShoppingCart WHERE client_id = {call.message.chat.id}')
            # conn.execute(f'DELETE FROM Clients WHERE telegram_id = {message.chat.id}')
        conn.commit()
        bot.send_message(call.message.chat.id, "Корзина успешно очищена!", reply_markup=After_clear_basket_keyb)
        msg = bot.send_message(call.message.chat.id, 'Корзина успешно очищена!')
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    """END Removing items from the cart END"""
    if call.data.split(':')[1] == 'Оформить заказ':
        Comment_keyb = InlineKeyboardMarkup()
        Comment_keyb.add(InlineKeyboardButton("Да", callback_data="user_basket:doit"))
        Comment_keyb.add(InlineKeyboardButton("Нет", callback_data="user_basket:refuse"))
        with conn:
            count_all_dishes = sum([i[0] for i in conn.execute(f'SELECT count FROM ShoppingCart WHERE  client_id= {call.message.chat.id}')])
        print("количество блюд в корзине", count_all_dishes)
        if count_all_dishes > 0:
            bot.send_message(call.message.chat.id, "Хотите указать адрес для текущего заказа, контактный телефон либо "
                                                   "добавить комментарий к заказу?", reply_markup=Comment_keyb)
        else:
            bot.send_message(call.message.chat.id, "Ваша корзина ещё пуста. Добавьте блюда в корзину.", reply_markup=Main_inline_keyb)
    if call.data.split(':')[1] == "doit":
        bot.answer_callback_query(call.id)  # подтверждаем нажатие
        bot.send_message(call.message.chat.id, "Укажите дополнительную информацию к своему заказу.",
                         reply_markup=telebot.types.ForceReply())  # просим пользователя оставить коммент и форсим в хендлер
    if call.data.split(':')[1] == "refuse":
        with conn:
            client_address = [i[3] for i in conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {call.message.chat.id}")][0]
            orders_id = [i for i in conn.execute(f'SELECT id FROM Orders WHERE  telegram_id = {call.message.chat.id}')][-1][0]
        markup_administration = InlineKeyboardMarkup()
        global information_in_admin_after_click_in_yes
        information_in_admin_after_click_in_yes = [i[0] for i in conn.execute(
            f'SELECT ShoppingCart.dish_id FROM ShoppingCart WHERE ShoppingCart.client_id = {call.message.chat.id} '
            f'AND ShoppingCart.count > 0')]
        information_in_admin_after_click_in_yes_count = [i[0] for i in conn.execute(
            f'SELECT ShoppingCart.count FROM ShoppingCart WHERE ShoppingCart.client_id = {call.message.chat.id} '
            f'AND ShoppingCart.count > 0')][0]
        information_in_admin_after_click_in_yes_price = [i[0] for i in conn.execute(
            f'SELECT ShoppingCart.total_price FROM ShoppingCart WHERE ShoppingCart.client_id = {call.message.chat.id} '
            f'AND ShoppingCart.count > 0')][0]
        markup_administration.add(InlineKeyboardButton('Поступил заказ',
                                                       callback_data=f'0:order_is_ready:{orders_id}:'
                                                                     f'{information_in_admin_after_click_in_yes}:'
                                                                     f'{information_in_admin_after_click_in_yes_count}:'
                                                                     f'{information_in_admin_after_click_in_yes_price}'))
        bot.send_message(call.message.chat.id, f'Ваша заявка оформлена! Ожидайте Ваш заказ по адресу: {client_address}:)', reply_markup=Main_inline_keyb)
        orders_table = "INSERT OR IGNORE INTO Orders (client_id, dish_ids, total_price, date, telegram_id, comment) values(?, ?, ?, ?, ?, ?)"
        current_datetime = DT.datetime.now()
        telegram_id = call.message.chat.id
        comment = "Без комментария"
        with conn:
            client_id = [i[0] for i in conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {call.message.chat.id}")][0]
            total_price = sum([i[3] for i in conn.execute(f'SELECT * FROM ShoppingCart WHERE client_id = {call.message.chat.id} AND count > 0')])
            print(total_price)
            dish_ids = ''
            list_orders_dish = [i[0] for i in conn.execute(f'SELECT dish_id FROM ShoppingCart WHERE client_id = {call.message.chat.id} AND count > 0')]
            # print(list_orders_dish)
            j = 0
            for i in list_orders_dish:
                print(i)
                count_orders = [i[0] for i in conn.execute(
                    f"SELECT ShoppingCart.count FROM ShoppingCart WHERE {int(i)} = ShoppingCart.dish_id AND ShoppingCart.count > 0")][0]
                dish_ids += str(i) + ':' + str(count_orders) + ', '
                j += 1
            conn.execute(orders_table, [client_id, dish_ids, total_price, current_datetime, telegram_id, comment])
        conn.commit()
        with conn:
            conn.execute(f'DELETE FROM ShoppingCart WHERE client_id = {call.message.chat.id}')
        conn.commit()
        admin_to_information = ''
        for i in conn.execute(
                f"SELECT Dish.name, ShoppingCart.count, ShoppingCart.client_id FROM Dish, ShoppingCart "
                f"WHERE ShoppingCart.client_id = {call.message.chat.id} AND Dish.id = ShoppingCart.dish_id"):
            admin_to_information += f'**НАЗВАНИЕ - {i[0]} КОЛ-ВО:{i[1]}**\n'
        global id_msg
        msge = (bot.send_message(chat_id='@restaurantletvin', text=f'Клиент заказал:\n{admin_to_information}',
                                 parse_mode="Markdown", reply_markup=markup_administration).message_id)
        message_dict_id.setdefault(msge, orders_id)
        with open(r'C:\Users\admin\MegaBot\id_message.json', 'w+') as file:
            json.dump(message_dict_id, file, indent=4, ensure_ascii=False)
        conn.commit()
    if call.data.split(':')[1] == 'order_is_ready':
        # print(call.data.split(':')[2])
        markup_yes_or_no = InlineKeyboardMarkup()
        markup_yes_or_no.add(InlineKeyboardButton('Да', callback_data=f'x:yes:{call.data.split(":")[2]}:{call.data.split(":")[3]}:{call.data.split(":")[4]}:{call.data.split(":")[5]}'), InlineKeyboardButton('Нет', callback_data='y:no'))
        bot.send_message(call.message.chat.id, 'Заказ готов к отправке клиенту?', reply_markup=markup_yes_or_no)
    if call.data.split(':')[1] == 'yes':
        print('ВОТ И ВСЕ', type(call.data.split(":")[3]))
        with open(r'C:\Users\admin\MegaBot\id_message.json', 'r') as file:
            request = json.load(file)
            for key, value in request.items():
                print(key)
                txt = ''
                result = information_in_admin_after_click_in_yes
                if value == int(call.data.split(':')[2]):
                    with conn:
                        for j in result:
                            list_informations_for_adm = [i for i in conn.execute(f'SELECT Dish.name FROM Dish WHERE id = {int(j)}')]
                            print("МАССИВВВ",list_informations_for_adm)
                            for i in list_informations_for_adm:
                                txt += f'Заказанное блюдо{i}\n'\
                                       f'Количество: {call.data.split(":")[4]}\n' \
                                       f'Цена:{call.data.split(":")[5]}'
                        msg_to_admin = f'Заказ успешно оформлен! {txt}'
                        bot.edit_message_text(msg_to_admin, call.message.chat.id, int(key))
                        bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data.split(':')[1] == "b3":
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Sub_inline_keyb)
    """___Обработка коллбэка от кнопки 'О нас'___"""
    if call.data.split(':')[1] == "txt2":
        global Reviews_inline_keyb
        Reviews_inline_keyb = InlineKeyboardMarkup()
        Reviews_inline_keyb.add(InlineKeyboardButton("Отзывы о ресторане", callback_data="review:r1"))
        # Reviews_inline_keyb.add(InlineKeyboardButton("Отзывы о еде", callback_data="review:r2"))
        Reviews_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        """START ФОТКИ интерьера рестика, использование метода send_media_group: 
        # получаем полный путь к файлу 
        # создаем список объектов InputMediaPhoto 
        # открываем файл в режиме чтения байтов и добавляем в список
        """
        files = os.listdir("photorest")
        photos = [file for file in files if file.endswith(".jpg")]  # фильтруем файлы по расширению .jpg
        media = [InputMediaPhoto(open(os.path.join("photorest", photo), "rb")) for photo in photos]
        bot.send_media_group(call.message.chat.id, media)
        """END ФОТКИ интерьера рестика"""
        about_restaurant = f"Здравствуйте, уважаемые Гости!\n «Лiтвiны» — ресторан современной белорусской кухни." \
                           f"В средние века предков белорусов называли литвинами.Трудолюбивое и любознательное население" \
                           f" из века в век выращивало рожь, овощи, фрукты. Все, что водилось в реках, озёрах, на болотах," \
                           f" в лесах, разнообразило питание.\nКонечно, мы учитываем современные тренды, но стараемся " \
                           f"использовать их именно в нашем национальном прочтении.\nМы стараемся, чтобы в наших " \
                           f"ресторанах восхищались гости нашей страны и гордились белорусы." \
                           f""
        info_rest = f"ТЦ Green City\n" \
                    f"Телефон: +375 44 519-11-11\n" \
                    f"Время работы: 11:00-23:00\n" \
                    f"Метро: Каменная горка\n" \
                    f"Адрес: Минск, ул. Притыцкого, 156/1\n"
        url_rest = "\U0001F30D https://litviny.by/rus/about"
        url2_rest = "https://www.instagram.com/litviny.by/"
        bot.send_message(call.message.chat.id, f"{about_restaurant}\n{info_rest}\nСайт: {url_rest}\n\nInstagram: {url2_rest}", parse_mode="Markdown", reply_markup=Reviews_inline_keyb)
    if call.data.split(':')[1] == "r1":
        AfterReview_inline_keyb = InlineKeyboardMarkup()
        AfterReview_inline_keyb.add(InlineKeyboardButton("Оставить отзыв", callback_data="feedback:r3"))
        AfterReview_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        result_card = ""
        for key, value in review_order_dict.items():
            result_card += f"\U0001F5E8{client_dict[value]}: '{key}'\n\n"
        print("СЛОВАРЬ С ОТЗЫВАМИ О ЗАКАЗАХ", result_card)
        if len(result_card) != 0:
            bot.send_message(call.message.chat.id, f"{result_card}", reply_markup=AfterReview_inline_keyb)
        else:
            bot.send_message(call.message.chat.id,
                             f"Отзывов еще нет. Вы можете оставить свой, если ранее офромляли заказ.",
                             reply_markup=AfterReview_inline_keyb)
    if call.data.split(':')[1] == "r3":
        MakeReviewError_inline_keyb = InlineKeyboardMarkup()
        MakeReviewError_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        MakeReviewError_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:txt2"))
        if call.message.chat.id in orders_telegram_id:  # если пользователь ранее делал заказы
            print("clients id telegram", call.message.chat.id)
            bot.answer_callback_query(call.id)  # подтвердить нажатие
            bot.send_message(call.message.chat.id, "Как вы оцениваете работу ресторана?", reply_markup=telebot.types.ForceReply())  # спрашиваем пользователя о его отзыве
        else:
            bot.send_message(call.message.chat.id, "Оставить отзыв о работе ресторана Вы сможете после оформления заказа с помощью нашаего чат-бота. Спасибо!",
                             reply_markup=MakeReviewError_inline_keyb)  # выдать клаву если пользователь ранее не делал заказов
    if call.data.split(':')[1] in ["profile", "to_profile"]:
        if call.data.split(':')[1] == "to_profile":
            global profile_edit_data
            profile_edit_data = {"Изменить имя": "edit:name",
                                 "Изменить телефон": "edit:phone_number",
                                 "Изменить адрес": "edit:delivery_adress",
                                 "Вернуться в меню": "menu:b1",
                                 "Показать корзину": "dish_card:basket2"}
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id  # id телеги пользователя
        cursor.execute("SELECT * FROM Clients WHERE telegram_id = ?", (user_id,))  # проверяем, есть ли запись о пользователе в БД
        row = cursor.fetchone()
        if row is None:  # если нет, то просим пользователя ввести свои данные/зарегистрироваться
            Reg_inline_keyb = InlineKeyboardMarkup()
            Reg_inline_keyb.add(InlineKeyboardButton("РЕГИСТРАЦИЯ", callback_data="prereg:pushreg"))
            Reg_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
            bot.send_message(call.message.chat.id, "Чтобы пользоваться чат-ботом, нужно пройти регистрацию.", reply_markup=Reg_inline_keyb)
        else:  # если есть, то показываем пользователю его текущие данные и предлагаем ему изменить их
            name, phone, address = row[1], row[2], row[3]
            bot.send_message(call.message.chat.id,
                             f"Ваш профиль:\nИмя: {name}\nТелефон: {phone}\nАдрес: {address}\n\nВы можете изменить любое из этих полей, нажав на соответствующую кнопку.",
                             reply_markup=create_edit_button(profile_edit_data))
    if call.data.split(':')[1] in field_dict:
        global field
        field = call.data.split(':')[1]
    if call.data.split(':')[0] == "edit":
        bot.answer_callback_query(call.id)  # подтверждаем нажатие
        bot.send_message(call.message.chat.id, f"Введите новое значение для поля '{field_dict[field]}'.", reply_markup=telebot.types.ForceReply())
    global reg_name, reg_phone_number, reg_delivery_adress  # значения регистрации по умолчанию
    if call.data.split(':')[1] == "pushreg":
        with conn:
            conn.execute("INSERT OR IGNORE INTO Clients (name, phone_number, delivery_adress, telegram_id) values(?, ?, ?, ?)", (reg_name, reg_phone_number, reg_delivery_adress, user_telegram_id))
        conn.commit()
        bot.answer_callback_query(call.id)  # подтверждаем нажатие
        bot.send_message(call.message.chat.id, "Заполните все поля формы и сохраните данные:", reply_markup=create_registration_keyb())
    if call.data.split(':')[1] in reg_field_dict:
        global reg_field
        reg_field = call.data.split(':')[1]
    if call.data.split(':')[0] == "reg":
        bot.answer_callback_query(call.id)  # подтверждаем нажатие
        bot.send_message(call.message.chat.id, f"Введите значение для поля '{reg_field_dict[reg_field]}'.", reply_markup=telebot.types.ForceReply())
    if call.data.split(':')[0] == "accept":
        with conn:
            conn.execute("INSERT OR IGNORE INTO Clients (name, phone_number, delivery_adress, telegram_id) values(?, ?, ?, ?)", (reg_name, reg_phone_number, reg_delivery_adress, user_telegram_id))
        conn.commit()
        # bot.send_message(call.message.chat.id, f"Данные для поля '{reg_field_dict[save_field]}' успешно сохранены.", reply_markup=create_registration_keyb())
        if reg_name != "Указать имя" and reg_phone_number != "Указать телефон" and len(reg_phone_number) == 13 and reg_delivery_adress != "Указать адрес":
            Success_reg_inline_keyb = InlineKeyboardMarkup()
            Success_reg_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"Вы успешно прошли регистрацию.\n"
                                                   f"Ваш профиль:\n"
                                                   f"Имя: {reg_name}\n"
                                                   f"Телефон: {reg_phone_number}\n"
                                                   f"Адрес: {reg_delivery_adress}\n\n"
                                                   f"Вы можете изменить любое из этих полей в своём профиле.",
                             reply_markup=Success_reg_inline_keyb)
        else:
            bot.send_message(call.message.chat.id, f"Введите корректные данные для всех полей и сохраните данные.", reply_markup=create_registration_keyb())
    if call.data.split(':')[1] == 'txt4':
        user_id = call.from_user.id  # id телеги пользователя
        cursor.execute("SELECT * FROM Clients WHERE telegram_id = ?", (user_id,))  # проверяем, есть ли запись о пользователе в БД
        row = cursor.fetchone()
        print(row)
        if row is None:  # если нет, то просим пользователя ввести свои данные/зарегистрироваться
            Reg_inline_keyb = InlineKeyboardMarkup()
            Reg_inline_keyb.add(InlineKeyboardButton("РЕГИСТРАЦИЯ", callback_data="prereg:pushreg"))
            Reg_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
            bot.send_message(call.message.chat.id, "Чтобы пользоваться чат-ботом, нужно пройти регистрацию.",
                             reply_markup=Reg_inline_keyb)
        else:
            with conn:
                ordered_dishes = [i[2] for i in cursor.execute(f"SELECT * FROM Orders WHERE telegram_id = {call.from_user.id}")]  # достаём из БД id-ки заказов
                total_price = [i[3] for i in cursor.execute(f"SELECT * FROM Orders WHERE telegram_id = {call.from_user.id}")]  # достаём из БД total_price заказов
                dish_count_dict = dict(zip(ordered_dishes, total_price))
                order_dates = [i[4] for i in cursor.execute(f"SELECT * FROM Orders WHERE telegram_id = {call.from_user.id}")]  # достаём из БД Дату
                result_dict = {}  # Создаем пустой словарь
                for i in range(len(order_dates)):  # Проходим по элементам списка и получаем ключ и значение из словаря a по индексу i
                    key = list(dish_count_dict.keys())[i]
                    value = list(dish_count_dict.values())[i]
                    result_dict[order_dates[i]] = [key, value]  # Добавляем в словарь пару ключ-значение, где ключ - элемент из списка b, а значение - список из ключа и значения из словаря
                print("СЛОВАРЬ ДАТА: АЙДИШКИ + СУММА", result_dict)  # {'2023-06-05 17:55:36.576892': ['25:2, 28:1, ', 30.0], '2023-06-05 17:58:32.619595': ['25:2, 29:2, ', 40.0]}
            text_card = 'Вот все Ваши заказы:\n'
            num = 1
            for key, value in result_dict.items():
                order_date = key[:16]
                text_card += f"{num}. Дата заказа: {order_date}:\n"
                for info in value[0].replace(" ", "").split(',')[:-1]:
                    print("info", info)
                    dish_name = [i for i in cursor.execute(f"SELECT name FROM Dish WHERE id = {info.split(':')[0]}")][0]
                    amount = info.split(':')[1]  # количество штук
                    text_card += f'- {dish_name[0]} - {amount} шт.\n'
                text_card += f"Сумма заказа: {value[1]} рублей.\n"
                num += 1
            bot.send_message(call.message.chat.id, f'{text_card}', reply_markup=Main_inline_keyb)
    """ADMINISTRATION"""
    if call.data.split(':')[1] == "addadmin":
        add_inline_keyb = InlineKeyboardMarkup()
        add_inline_keyb.add(InlineKeyboardButton("Добавить данные о новом администраторе", callback_data="addm:adminid"))
        add_inline_keyb.add(InlineKeyboardButton("Вернуться назад↩ ", callback_data="addm:backmenu"))
        bot.send_message(call.message.chat.id, "Добавьте данные о новом администраторе", reply_markup=add_inline_keyb)
    if call.data.split(':')[1] == "backmenu":
        bot.send_message(call.message.chat.id, "Добавьте данные о новом администраторе", reply_markup=Admin_keyb_lvl1)
    if call.data.split(":")[1] == "adminid":
        bot.send_message(call.message.chat.id, "Введите telegram id нового администратора", reply_markup=telebot.types.ForceReply())
    if call.data.split(':')[1] == "admin_orders_rev":
        try:
            with conn:
                review_id = [i[0] for i in conn.execute(f"SELECT * FROM Reviews")]
                review_text = [i[1] for i in conn.execute(f"SELECT * FROM Reviews")]
                client_id3 = [i[3] for i in conn.execute(f"SELECT * FROM Reviews")]
                status_review = [i[6] for i in conn.execute(f"SELECT * FROM Reviews")]
                client_name = [i[1] for i in conn.execute(f"SELECT * FROM Clients")]
                client_id4 = [i[0] for i in conn.execute(f"SELECT * FROM Clients")]
                client_dict2 = dict(zip(client_id4, client_name))
                # Создаем пустой результирующий словарь для вывода карточки для админа следующего вида:
                # {2: ['Еда вкусная, доставка быстрая!', 142, 'YES'], }
                global review_result_dict
                review_result_dict = {}
                for key, value1, value2, value3 in zip(review_id, review_text, client_id3, status_review):
                    review_result_dict[key] = [value1, value2, value3]
                print("СЛОВАРЬ для вывода карточки отзывов для админа", review_result_dict)
        except Exception as e:
            print(e)
        global result_card_for_admin
        result_card_for_admin = ""
        for key, value in review_result_dict.items():
            result_card_for_admin += f"{key}. \U0001F5E8{client_dict2[value[1]]}: '{value[0]}'\n\n"
        if len(result_card_for_admin) != 0:
            bot.send_message(call.message.chat.id, f"Отзывы пользователей:\n"
                                                   f"{result_card_for_admin}",
                             reply_markup=create_admin_review_keyb(review_result_dict))
        else:
            bot.send_message(call.message.chat.id, f"Отзывов нет.", reply_markup=Admin_keyb_lvl2)
    bot.answer_callback_query(call.id)  # подтверждаем нажатие
    if call.data.split(':')[0] == "-edit_review":  # если нажата кнопка "Отклонить"
        review_result_dict[int(call.data.split(':')[1][1:])][2] = "NO"
        try:
            with conn:
                conn.execute(f"UPDATE Reviews SET accept = ? WHERE id = ?",
                             (review_result_dict[int(call.data.split(':')[1][1:])][2], int(call.data.split(':')[1][1:])))
                conn.execute(f"UPDATE Reviews SET admin_id = ? WHERE id = ?",
                             (call.message.chat.id, int(call.data.split(':')[1][1:])))
            conn.commit()
        except Exception as e:
            print(e)
        bot.edit_message_text(f"{result_card_for_admin}", call.message.chat.id, call.message.message_id,
                                  reply_markup=create_admin_review_keyb(review_result_dict))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Статуст отзыва № {int(call.data.split(':')[1][1:])}. "
                                                     f"успешно изменён на 'NO'")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[0] == "+edit_review":  # если нажата кнопка "Утвердить"
        print("ПРИНЯТЬ КОЛБЭКДАТА", int(call.data.split(':')[1][1:]))
        review_result_dict[int(call.data.split(':')[1][1:])][2] = "YES"
        try:
            with conn:
                conn.execute(f"UPDATE Reviews SET accept = ? WHERE id = ?",
                             (review_result_dict[int(call.data.split(':')[1][1:])][2], int(call.data.split(':')[1][1:])))
                conn.execute(f"UPDATE Reviews SET admin_id = ? WHERE id = ?",
                             (call.message.chat.id, int(call.data.split(':')[1][1:])))
            conn.commit()
        except Exception as e:
            print(e)
        bot.edit_message_text(f"{result_card_for_admin}", call.message.chat.id, call.message.message_id,
                              reply_markup=create_admin_review_keyb(
                                  review_result_dict))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Статуст отзыва № {int(call.data.split(':')[1][1:])}. успешно изменён на 'YES'")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[1] == "admin_panel":
        bot.send_message(call.message.chat.id,
                         "Админ-панель 2 уровня.\n"
                         "Функционал:\n"
                         "- Добавление нового блюда;\n"
                         "- Постановка блюда на СТОП\n"
                         "- Обработка отзывов.", reply_markup=Admin_keyb_lvl2)
    if call.data.split(':')[1] == "admin_dishes_rev":
        try:
            with conn:
                review_dish_id = [i[0] for i in conn.execute(f"SELECT * FROM ReviewDish")]
                review_dish_text = [i[1] for i in conn.execute(f"SELECT * FROM ReviewDish")]
                client_dish_id = [i[2] for i in conn.execute(f"SELECT * FROM ReviewDish")]
                status_review_dish = [i[4] for i in conn.execute(f"SELECT * FROM ReviewDish")]
                dish_id_id = [i[3] for i in conn.execute(f"SELECT * FROM ReviewDish")]
                client_name = [i[1] for i in conn.execute(f"SELECT * FROM Clients")]
                client_id4 = [i[0] for i in conn.execute(f"SELECT * FROM Clients")]
                client_dict2 = dict(zip(client_id4, client_name))
                # Создаем пустой результирующий словарь для вывода карточки для админа следующего вида:
                # {3: ['Super', 142, None, 25], 4: ['Вельмі смачна', 142, None, 9]}
                global review_dish_result_dict
                review_dish_result_dict = {}
                for key, value1, value2, value3, value4 in zip(review_dish_id, review_dish_text, client_dish_id, status_review_dish, dish_id_id):
                    review_dish_result_dict[key] = [value1, value2, value3, value4]
                print("СЛОВАРЬ для вывода карточки отзывов о блюдах для админа", review_dish_result_dict)
        except Exception as e:
            print(e)
        global result_card_for_admin2
        result_card_for_admin2 = ""
        for key, value in review_dish_result_dict.items():
            rev_dish_name = [i[1] for i in conn.execute(f"SELECT * FROM Dish WHERE id = {value[3]}")][0]
            print(rev_dish_name)
            result_card_for_admin2 += f"{key}. {rev_dish_name}: '{value[0]}' (\U0001F5E8{client_dict2[value[1]]})\n\n"
        if len(result_card_for_admin2) != 0:
            bot.send_message(call.message.chat.id, f"Отзывы пользователей:\n"
                                                   f"{result_card_for_admin2}",
                             reply_markup=create_admin_reviewdish_keyb(review_dish_result_dict))
        else:
            bot.send_message(call.message.chat.id, f"Отзывов нет.", reply_markup=Admin_keyb_lvl2)

            bot.answer_callback_query(call.id)  # подтверждаем нажатие
    bot.answer_callback_query(call.id)  # подтверждаем нажатие
    if call.data.split(':')[0] == "-edit_reviewdish":  # если нажата кнопка "Отклонить"
        review_dish_result_dict[int(call.data.split(':')[1][2:])][2] = "NO"
        try:
            with conn:
                conn.execute(f"UPDATE ReviewDish SET accept = ? WHERE id = ?",
                             (review_dish_result_dict[int(call.data.split(':')[1][2:])][2], int(call.data.split(':')[1][2:])))
                conn.execute(f"UPDATE ReviewDish SET admin_id = ? WHERE id = ?",
                             (call.message.chat.id, int(call.data.split(':')[1][2:])))
            conn.commit()
        except Exception as e:
            print(e)
        bot.edit_message_text(f"{result_card_for_admin2}", call.message.chat.id, call.message.message_id,
                              reply_markup=create_admin_reviewdish_keyb(
                                  review_dish_result_dict))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Статуст отзыва № {int(call.data.split(':')[1][2:])}. "
                                                     f"успешно изменён на 'NO'")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[0] == "+edit_reviewdish":  # если нажата кнопка "Утвердить"
        review_dish_result_dict[int(call.data.split(':')[1][2:])][2] = "YES"
        try:
            with conn:
                conn.execute(f"UPDATE ReviewDish SET accept = ? WHERE id = ?",
                             (review_dish_result_dict[int(call.data.split(':')[1][2:])][2],
                              int(call.data.split(':')[1][2:])))
                conn.execute(f"UPDATE ReviewDish SET admin_id = ? WHERE id = ?",
                             (call.message.chat.id, int(call.data.split(':')[1][2:])))
            conn.commit()
        except Exception as e:
            print(e)
        bot.edit_message_text(f"{result_card_for_admin2}", call.message.chat.id, call.message.message_id,
                              reply_markup=create_admin_reviewdish_keyb(
                                  review_dish_result_dict))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Статуст отзыва № {int(call.data.split(':')[1][2:])}. "
                                                     f"успешно изменён на 'NO'")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[1] == "admin_dish_add":
        global result_card_for_admin3
        result_card_for_admin3 = ""
        # for key, value in default_dict_add_dish.items():
        #     result_card_for_admin3 += f"{key}: {value}\n"
        bot.send_message(call.message.chat.id, f"Карточка нового блюда.\n"
                                               f"Выберите поле и последовательно внесите необходимые данные.",
                         reply_markup=create_admin_adddish_keyb(default_dict_add_dish))
    if call.data.split(':')[0] == "admin_add_new_dish":
        bot.answer_callback_query(call.id)  # подтвердить нажатие
        global question_num
        question_num = int(call.data.split(':')[1][9:])
        print(question_num)
        question = default_dict_add_dish[question_num][2]
        print(question)
        if question in [v[2] for k, v in default_dict_add_dish.items()][:6]:  # запрашиваем у админа сведения для для заполнения таблицы Dish
            bot.send_message(call.message.chat.id,
                             f"{question}",
                             reply_markup=telebot.types.ForceReply())  # соотв-й вопрос админу
        if question == [v[2] for k, v in default_dict_add_dish.items()][6]:  # выбор меры измерения блюда
            measure_keyboard = InlineKeyboardMarkup(row_width=2)
            measure_keyboard.add(InlineKeyboardButton("гр.", callback_data='measure:gr'),
                                 InlineKeyboardButton("мл.", callback_data='measure:ml'))
            bot.send_message(call.message.chat.id, f"{question}", reply_markup=measure_keyboard)  # запрашиваем у админа выбор
        if question == [v[2] for k, v in default_dict_add_dish.items()][7]:  # выбор категории
            category_question_keyboard = InlineKeyboardMarkup(row_width=2)
            [category_question_keyboard.add(InlineKeyboardButton(key, callback_data=f"qn_cat:{key}:{value}")) for key, value in
             column_dict.items()]
            bot.send_message(call.message.chat.id, f"{question}", reply_markup=category_question_keyboard)  # запрашиваем у админа выбор
        if question == [v[2] for k, v in default_dict_add_dish.items()][8]:  # выбор субкатегории
            sub_category_question_keyboard = InlineKeyboardMarkup(row_width=2)
            [sub_category_question_keyboard.add(InlineKeyboardButton(key, callback_data=f"qn_subcat:{key}:{value}")) for key, value in
             subcat_dict2.items()]
            bot.send_message(call.message.chat.id, f"{question}", reply_markup=sub_category_question_keyboard)  # запрашиваем у админа фото
        if question == [v[2] for k, v in default_dict_add_dish.items()][9]:  # добавить фото
            bot.send_message(call.message.chat.id,
                             f"{question}",
                             reply_markup=telebot.types.ForceReply())  # соотв-й вопрос админу
    if call.data.split(':')[0] == "measure":
        bot.answer_callback_query(call.id)  # подтвердить нажатие
        if call.data.split(':')[1] == "gr":
            default_dict_add_dish[7][1] = "гр."
            bot.send_message(call.message.chat.id, f"Карточка нового блюда:", reply_markup=create_admin_adddish_keyb(
                default_dict_add_dish))  # обновляем сообщение с клавиатурой
            msg = bot.send_message(call.message.chat.id, f"Данные добавлены в карточку")
            time.sleep(3)
            bot.delete_message(call.message.chat.id, msg.message_id)
        if call.data.split(':')[1] == "ml":
            default_dict_add_dish[7][1] = "мл."
            bot.send_message(call.message.chat.id, f"Карточка нового блюда:", reply_markup=create_admin_adddish_keyb(
                default_dict_add_dish))  # обновляем сообщение с клавиатурой
            msg = bot.send_message(call.message.chat.id, f"Данные добавлены в карточку")
            time.sleep(3)
            bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[0] == "qn_cat":
        print(call.data.split(':')[0])
        bot.answer_callback_query(call.id)  # подтвердить нажатие
        category_id_qn, category_name_qn = call.data.split(':')[2], call.data.split(':')[1]
        default_dict_add_dish[8][1] = f"{category_id_qn}: {category_name_qn}"
        bot.send_message(call.message.chat.id, f"Карточка нового блюда:", reply_markup=create_admin_adddish_keyb(default_dict_add_dish))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Данные добавлены в карточку")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[0] == "qn_subcat":
        print(call.data.split(':')[0])
        bot.answer_callback_query(call.id)  # подтвердить нажатие
        subcategory_id_qn, subcategory_name_qn = call.data.split(':')[2], call.data.split(':')[1]
        default_dict_add_dish[9][1] = f"{subcategory_id_qn}: {subcategory_name_qn}"
        bot.send_message(call.message.chat.id, f"Карточка нового блюда:", reply_markup=create_admin_adddish_keyb(default_dict_add_dish))  # обновляем сообщение с клавиатурой
        msg = bot.send_message(call.message.chat.id, f"Данные добавлены в карточку")
        time.sleep(3)
        bot.delete_message(call.message.chat.id, msg.message_id)
    if call.data.split(':')[1] == "save_new_dish":
        print("SAVE NEW DISH")
        d_name = default_dict_add_dish[1][1]
        d_description = default_dict_add_dish[2][1]
        d_photo = default_dict_add_dish[10][1]
        d_price = float(default_dict_add_dish[3][1])
        d_time = int(default_dict_add_dish[4][1])
        d_weight = float(default_dict_add_dish[5][1])
        d_unit = default_dict_add_dish[7][1]
        d_is_stop = "False"
        d_count = int(default_dict_add_dish[6][1])
        d_category_id = int(default_dict_add_dish[8][1].split(":")[0])
        d_subcategory_id = int(default_dict_add_dish[9][1].split(":")[0])
        print(default_dict_add_dish)
        with conn:
            conn.execute("INSERT INTO Dish (name, description, photo, price, time, weight, unit, is_stop, count, category_id, subcategory_id) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (d_name, d_description, d_photo, d_price, d_time, d_weight, d_unit, d_is_stop, d_count, d_category_id, d_subcategory_id))  # добавьте новую запись в таблицу "Отзывы"
        conn.commit()  # сохраняем изменения в базе данных

        bot.send_message(call.message.chat.id, "Новое блюдо добавлено в базу данных", reply_markup=Admin_keyb_lvl2)
    if call.data.split(':')[1] == "admin_dish_stop":
        try:
            with conn:
                dish_id = [i[0] for i in conn.execute(f"SELECT * FROM Dish")]
                dish_name = [i[1] for i in conn.execute(f"SELECT * FROM Dish")]
                status_dish = [i[8] for i in conn.execute(f"SELECT * FROM Dish")]
                global status_dish_result_dict
                status_dish_result_dict = {}
                for key, value1, value2 in zip(dish_id, dish_name, status_dish):
                    status_dish_result_dict[key] = [value1, value2]
                print("СЛОВАРЬ статуса блюд для админа", status_dish_result_dict)
        except Exception as e:
            print(e)
        bot.send_message(call.message.chat.id, f"Изменение статуса блюда:", reply_markup=create_admin_stop_dish_keyboard(status_dish_result_dict))
    if call.data.split(':')[0] == "stop_dish":  # если нажата кнопка "Изменить"
        print(call.data.split(':')[1])
        if call.data.split(':')[1] == "В продаже":
            status_dish_result_dict[int(call.data.split(':')[2])][1] = "Не продается"
            try:
                with conn:
                    conn.execute(f"UPDATE Dish SET is_stop = ? WHERE id = ?",
                                 (status_dish_result_dict[int(call.data.split(':')[2])][1], int(call.data.split(':')[2])))
                conn.commit()
            except Exception as e:
                print(e)
            bot.edit_message_text(f"Изменение статуса блюда:", call.message.chat.id, call.message.message_id,
                                  reply_markup=create_admin_stop_dish_keyboard(
                                      status_dish_result_dict))  # обновляем сообщение с клавиатурой
            msg_status = bot.send_message(call.message.chat.id, f"Статус для блюда {call.data.split(':')[2]} обновлён")
            time.sleep(3)
            bot.delete_message(call.message.chat.id, msg_status.message_id)
        if call.data.split(':')[1] == "Не продается":
            status_dish_result_dict[int(call.data.split(':')[2])][1] = "В продаже"
            try:
                with conn:
                    conn.execute(f"UPDATE Dish SET is_stop = ? WHERE id = ?",
                                 ("В продаже", int(call.data.split(':')[2])))
                conn.commit()
            except Exception as e:
                print(e)
            bot.edit_message_text(f"Изменение статуса блюда:", call.message.chat.id, call.message.message_id,
                                  reply_markup=create_admin_stop_dish_keyboard(status_dish_result_dict))  # обновляем сообщение с клавиатурой
            msg_status = bot.send_message(call.message.chat.id, f"Статус для блюда {call.data.split(':')[2]} обновлён")
            time.sleep(3)
            bot.delete_message(call.message.chat.id, msg_status.message_id)


# обработка ответа пользователя на вопрос о его отзыве на работу ресторана с последующей запись в БД
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ["Как вы оцениваете работу ресторана?"])
def handle_review_answer(message):
    client_id = [i[0] for i in conn.execute(f"SELECT id FROM Clients WHERE telegram_id = {message.chat.id}")][0]
    orders_id = [i[0] for i in conn.execute(f"SELECT id FROM Orders WHERE telegram_id = {message.chat.id}")][-1] # id последнего заказа из БД
    print("айди юзера", client_id, "id последнего заказа из БД", orders_id)
    dish_id = None
    review_order = message.text  # текст отзыва пользователя
    review_dish = ""
    with conn:
        conn.execute("INSERT INTO Reviews (review_order, review_dish, client_id, orders_id, dish_id) VALUES (?, ?, ?, ?, ?)",
                     (review_order, review_dish, client_id, orders_id, dish_id)) # добавьте новую запись в таблицу "Отзывы"
    conn.commit()  # сохраняем изменения в базе данных
    bot.send_message(message.chat.id, "Спасибо за Ваш отзыв!", reply_markup=Main_inline_keyb)


# обработка ответа пользователя на вопрос о его отзыве на блюдо с последующей записью в БД
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ["Понравилось ли Вам данное блюдо?"])
def handle_dish_review_answer(message):
    client_id = [i[0] for i in conn.execute(f"SELECT id FROM Clients WHERE telegram_id = {message.chat.id}")][0]
    orders_id = [i[0] for i in conn.execute(f"SELECT id FROM Orders WHERE telegram_id = {message.chat.id}")][-1] # id последнего заказа из БД
    print("айди юзера", client_id, "id последнего заказа из БД", orders_id)
    dish_id = dish_id_from_card
    review_dish = message.text  # текст отзыва пользователя
    with conn:
        conn.execute("INSERT INTO ReviewDish (review_dish, client_id, dish_id) VALUES (?, ?, ?)",
                     (review_dish, client_id, dish_id)) # добавьте новую запись в таблицу "Отзывы"
    conn.commit()  # сохраняем изменения в базе данных
    bot.send_message(message.chat.id, "Спасибо за Ваш отзыв!", reply_markup=Main_inline_keyb)


# обрабатываем ответ пользователя на вопрос о его имени пользователя/телефоне/адресе {field} при их изменении
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in [f"Введите новое значение для поля '{field_dict[field]}'."])
def handle_name_answer(message):
    global field, field_dict
    # message.from_user.id - это telegram id, message.text - введенные пользователем данные
    with conn:
        # добавляем новую запись в таблицу "Clients" с id телеги и именем пользователя/телефоном/адресом {field}
        conn.execute(f"UPDATE Clients SET {field} = ? WHERE telegram_id = ?", (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(message.chat.id, f"Вы успешно изменили {field_dict[field]}.", reply_markup=create_edit_button(profile_edit_data))


# обрабатываем ответы пользователя при регистрации на вопросы о его имени пользователя/телефоне/адресе reg_field_dict[reg_field]
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in [f"Введите значение для поля '{reg_field_dict[reg_field]}'.", f"Введите корректные данные для всех полей и сохраните данные."])
def handle_reg_answer(message):
    global reg_name, reg_phone_number, reg_delivery_adress  # значения регистрации по умолчанию
    if reg_field == 'name':
        reg_name = message.text
    if reg_field == 'phone_number':
        reg_phone_number = message.text
    if reg_field == 'delivery_adress':
        reg_delivery_adress = message.text
    bot.send_message(message.chat.id, f'''Вы успешно изменили поле "{reg_field_dict[reg_field]}".\nЗаполните все поля формы и сохраните данные:''', reply_markup=create_registration_keyb())


# обработка ответа пользователя на предложение оставить коммент о текущем заказе с последующей записью в БД Orders
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ["Укажите дополнительную информацию к своему заказу."])
def handle_order_answer(message):
    orders_table = "INSERT OR IGNORE INTO Orders (client_id, dish_ids, total_price, date, telegram_id, comment) values(?, ?, ?, ?, ?, ?)"
    total_price = [i[0] for i in conn.execute(
        f'SELECT total_price FROM ShoppingCart WHERE client_id = {message.chat.id} AND count > 0')]
    current_datetime = DT.datetime.now()
    telegram_id = message.chat.id
    comment = message.text
    with conn:
        client_id = [i[0] for i in conn.execute(f"SELECT * FROM Clients WHERE telegram_id = {message.chat.id}")][0]
        dish_ids = ''
        list_orders_dish = [i[0] for i in conn.execute(
            f'SELECT ShoppingCart.dish_id FROM ShoppingCart WHERE ShoppingCart.client_id = {message.chat.id} AND ShoppingCart.count > 0')]
        # print(list_orders_dish)
        j = 0
        for i in list_orders_dish:
            print(i)
            count_orders = [i[0] for i in conn.execute(
                f"SELECT ShoppingCart.count FROM ShoppingCart WHERE {int(i)} = ShoppingCart.dish_id AND ShoppingCart.count > 0")][0]
            dish_ids += str(i) + ':' + str(count_orders) + ', '
            j += 1
        conn.execute(orders_table, [client_id, dish_ids, total_price, current_datetime, telegram_id, comment])
    conn.commit()
    with conn:
        conn.execute(f'DELETE FROM ShoppingCart WHERE client_id = {message.chat.id}')
    conn.commit()
    bot.send_message(message.chat.id, 'Спасибо за комментарий! Постараемся учесть Ваши пожелания.\n'
                                      'Ваша заявка оформлена! Ожидайте Ваш заказ :) ', reply_markup=Main_inline_keyb)
    orders_id = [i for i in conn.execute(f'SELECT id FROM Orders WHERE  telegram_id = {message.chat.id}')][-1][0]
    print(orders_id)
    markup_administration = InlineKeyboardMarkup()
    markup_administration.add(InlineKeyboardButton('Поступил заказ', callback_data=f'0:order_is_ready:{orders_id}'))
    admin_to_information = ''
    for i in conn.execute(
            f"SELECT Dish.name, ShoppingCart.count FROM Dish, ShoppingCart WHERE ShoppingCart.client_id = {message.chat.id} "
            f"AND Dish.id = ShoppingCart.dish_id"):
        admin_to_information += f'**НАЗВАНИЕ - {i[0]} КОЛ-ВО:{i[1]}**\n'
    bot.send_message(chat_id='@restaurantletvin', text=f'Клиент заказал:\n{admin_to_information}',
                     parse_mode="Markdown", reply_markup=markup_administration)
    conn.execute(f'DELETE FROM ShoppingCart WHERE client_id = {message.chat.id}')


@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ["Введите telegram id нового администратора"])
def handler_admin_first_answer(message):
    print("Шляпа1")
    admin_table = "INSERT OR IGNORE INTO BotAdmins (telegram_id ,phone_number, position, first_name, last_name) values (?, ?, ?, ?, ?)"
    global tg_id
    tg_id = message.text
    first_name, last_name, phone_number, position = '', '', '', ''
    # add_adm = user_id
    with conn:
        conn.execute(admin_table, [tg_id, phone_number, position, first_name, last_name])
    conn.commit()
    bot.send_message(message.chat.id, "Введите имя нового администратора", reply_markup=telebot.types.ForceReply())


@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ["Введите имя нового администратора"])
def handler_admin_first_answer(message):
    print(tg_id, "Шляпа2")
    first_name = message.text
    with conn:
        conn.execute(f"UPDATE BotAdmins SET first_name = ? WHERE telegram_id = ?", (first_name, tg_id))
    conn.commit()
    bot.send_message(message.chat.id, "Введите фамилию нового администратора", reply_markup=telebot.types.ForceReply())


@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ["Введите фамилию нового администратора"])
def handler_admin_last_answer(message):
    last_name = message.text
    with conn:
        conn.execute(f"UPDATE BotAdmins SET last_name = ? WHERE telegram_id = ?", (last_name, tg_id))
    conn.commit()
    bot.send_message(message.chat.id, "Введите номер телефона нового администратора", reply_markup=telebot.types.ForceReply())


@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ["Введите номер телефона нового администратора"])
def handler_admin_last_answer(message):
    phone = message.text
    with conn:
        conn.execute(f"UPDATE BotAdmins SET phone_number = ? WHERE telegram_id = ?", (phone, tg_id))
    conn.commit()
    bot.send_message(message.chat.id, 'Укажите должность администратора', reply_markup=telebot.types.ForceReply())


@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in ['Укажите должность администратора'])
def handler_admin_last_answer(message):
    position = message.text
    with conn:
        conn.execute(f"UPDATE BotAdmins SET position = ? WHERE telegram_id = ?", (position, tg_id))
    conn.commit()
    bot.send_message(message.chat.id, "Админиcтратор успешно добавлен ", reply_markup=Admin_keyb_lvl1)


question_list = [v[2] for k, v in default_dict_add_dish.items()]
print(question_list[:6])
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text in question_list[:6])
def handler_admin_last_answer(message):
    global default_dict_add_dish
    new_dish_field = message.text
    default_dict_add_dish[question_num][1] = new_dish_field
    print(default_dict_add_dish)
    bot.send_message(message.chat.id, f"Карточка нового блюда:", reply_markup=create_admin_adddish_keyb(default_dict_add_dish))  # обновляем сообщение с клавиатурой
    msg = bot.send_message(message.chat.id, f"Данные добавлены в карточку")
    time.sleep(3)
    bot.delete_message(message.chat.id, msg.message_id)


@bot.message_handler(content_types=['text', 'photo'], func=lambda message: message.reply_to_message and message.reply_to_message.text == "Пришлите фотографию блюда")
def handle_photo_and_text(message):
    if message.text:  # если сообщение содержит текст
        bot.reply_to(message, 'Пришлите фотографию блюда', reply_markup=telebot.types.ForceReply())  # отправляем ответ пользователю
    elif message.photo:  # если сообщение содержит фотографию
        file_id = message.photo[-1].file_id  # получаем идентификатор файла
        file_info = bot.get_file(file_id)  # получаем информацию о файле
        file_path = file_info.file_path  # получаем путь к файлу
        print(str(int(dish_ids[-1]) + 1))
        print(file_id, file_info, file_path)
        # file_name = os.path.basename(file_path)  # получаем имя файла
        photo_file_name = str(int(dish_ids[-1]) + 1) + ".jpg"  # название фотки = "айди последнего блюда в БД + 1"
        downloaded_file = bot.download_file(file_path)  # скачиваем файл
        if not os.path.exists(PHOTO_DIR):  # проверяем, существует ли директория для сохранения фотографий
            os.makedirs(PHOTO_DIR)  # если нет, то создаем ее
        with open(os.path.join(PHOTO_DIR, photo_file_name), 'wb') as f:  # открываем файл для записи в бинарном режиме
            f.write(downloaded_file)  # записываем скачанный файл
        global default_dict_add_dish
        new_dish_field = photo_file_name
        default_dict_add_dish[question_num][1] = new_dish_field
        bot.send_message(message.chat.id, f"Карточка нового блюда:", reply_markup=create_admin_adddish_keyb(
            default_dict_add_dish))  # обновляем сообщение с клавиатурой
        msg1 = bot.reply_to(message, 'Фото успешно сохранено!')  # отправляем ответ пользователю
        time.sleep(3)
        bot.delete_message(message.chat.id, msg1.message_id)


print("Ready")
bot.infinity_polling(none_stop=True, interval=0)