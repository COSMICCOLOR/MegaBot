import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import sqlite3
import os
import array, gspread, requests, subprocess, datetime, uuid
import datetime as DT
import time


# logfile = str(datetime.date.today()) + '.log' # формируем имя лог-файла
token = '6112420224:AAFd0gDtUiAC2qqWo4osq82D6qyGH07c_UY'
bot = telebot.TeleBot(token)
conn = sqlite3.connect('restaurant1.db', check_same_thread=False)
markdown = """
    *bold text*
    _italic text_
    [text](URL)
    """

global dish_dict

try:
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
        data = conn.execute("SELECT * FROM Dish")
        print(data.fetchall())
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Dish")
        data2 = cursor.fetchall()  # fetchone
        dish_names = [i[1] for i in conn.execute(f"SELECT * FROM Dish")]
        dish_cat_ids = [str(i[11]) for i in conn.execute(f"SELECT * FROM Dish")]
        dish_ids = [str(i[0]) for i in conn.execute(f"SELECT * FROM Dish")]
        dish_dict2 = dict(zip(dish_names, dish_ids))
        dish_dict = dict(zip(dish_names, dish_cat_ids))
        dish_all_dict = dict(zip(dish_names, [[i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[9], i[0]] for i in conn.execute(f"SELECT * FROM Dish")]))
except Exception as e:
    print(e)

try:
    with conn:
        data = conn.execute("SELECT * FROM Reviews")
        print(data.fetchall())
        review_order = [i[1] for i in conn.execute(f"SELECT * FROM Reviews WHERE accept = 'True'")]
        review_dish = [i[2] for i in conn.execute(f"SELECT * FROM Reviews")]
        client_id = [i[3] for i in conn.execute(f"SELECT * FROM Reviews WHERE accept = 'True'")]
        orders_id = [i[4] for i in conn.execute(f"SELECT * FROM Reviews")]
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

# Создаем клавиатуру и кнопки для главного меню ADMIN-панели
Admin_keyb = InlineKeyboardMarkup()
Admin_keyb.add(InlineKeyboardButton("Добавить администратора➕", callback_data="admin:addadmin"))
Admin_keyb.add(InlineKeyboardButton("Удалить администратора➖", callback_data="admin:deladmin"))
Admin_keyb.add(InlineKeyboardButton("Редактировать профиль администратора🛠️", callback_data="admin:redadmin"))

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
        row = [i[1] for i in conn.execute("SELECT * FROM BotAdmins WHERE position = 'main admin'")]
    if user_id not in row:  # проверяем id на пригодность
        bot.send_message(message.chat.id, "Вы не являетесь администратором.\nВыберите лучше покушать\U0001F609 ",
                         reply_markup=Main_inline_keyb)
    else:  # если есть, то показываем админу клаву для управления админкой
        bot.send_message(message.chat.id,
                         "Админ-панель 1 уровня.\nФункционал: добавление, изменение и удаление админов 2 уровня.", reply_markup=Admin_keyb)


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
            dish_feedback = [i[1] for i in conn.execute(f"SELECT * FROM ReviewDish WHERE dish_id = {call.data.split(':')[2]} AND accept = 'True'")]
            cl_id_feedback = [i[2] for i in conn.execute(f"SELECT * FROM ReviewDish WHERE dish_id = {call.data.split(':')[2]} AND accept = 'True'")]
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
        for i in range(len(dish_name_list)):  # Проходим по элементам списка и Получаем ключ и значение из словаря a по индексу i
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
        """!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"""
    # if call.data.split(':')[1] in dish_names:
    #     print("lineeeee 408-409 call.data.split(':')[1] in dish_names", call.data.split(":")[0])
    #     conn.execute(f'DELETE FROM ShoppingCart WHERE ShoppingCart.dish_id = {call.data.split(":")[0]}')
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
        bot.send_message(call.message.chat.id, f'Ваша заявка оформлена! Ожидайте Ваш заказ по адресу: {client_address} :)', reply_markup=Main_inline_keyb)
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
# END code serezha + Dima_______________________________________________________________________________________________

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
                             reply_markup=Main_inline_keyb)
    if call.data.split(':')[1] == "r3":
        MakeReviewError_inline_keyb = InlineKeyboardMarkup()
        MakeReviewError_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        MakeReviewError_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:txt2"))
        if call.message.chat.id in orders_telegram_id:
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
                order_dates = [i[4] for i in cursor.execute(f"SELECT * FROM Orders WHERE telegram_id = {call.from_user.id}")]  # достаём из БД Дату и id-ки заказов
                ordered_dishes = [i[2] for i in cursor.execute(f"SELECT * FROM Orders WHERE telegram_id = {call.from_user.id}")]  # достаём из БД Дату и id-ки заказов
                date_dish_dict = dict(zip(order_dates, ordered_dishes))
            # orders_client = [i for i in cursor.execute(f"SELECT date, dish_ids FROM Orders WHERE telegram_id = {call.from_user.id}")]  # достаём из БД Дату и id-ки заказов
            print("ИСТОРИЯ ЗАКАЗОВ", date_dish_dict)
            text_card = 'Вот все Ваши заказы:\n'
            num = 1
            for key, value in date_dish_dict.items():
                order_date = key[:16]
                text_card += f"{num}. Дата заказа: {order_date}:\n"
                for info in value.replace(" ", "").split(',')[:-1]:
                    print("info", info)
                    dish_name = [i for i in cursor.execute(f"SELECT name FROM Dish WHERE id = {info.split(':')[0]}")][0]
                    amount = info.split(':')[1]  # количество штук
                    text_card += f'- {dish_name[0]} - {amount} шт.\n'
                num += 1
            bot.send_message(call.message.chat.id, f'{text_card}')

    if call.data.split(':')[1] == "addadmin":
        add_inline_keyb = InlineKeyboardMarkup()
        add_inline_keyb.add(InlineKeyboardButton("Добавить данные о новом администраторе", callback_data="addm:adminid"))
        add_inline_keyb.add(InlineKeyboardButton("Вернуться назад↩ ", callback_data="addm:backmenu"))
        bot.send_message(call.message.chat.id, "Добавьте данные о новом администраторе", reply_markup=add_inline_keyb)
    if call.data.split(':')[1] == "backmenu":
        bot.send_message(call.message.chat.id, "Добавьте данные о новом администраторе", reply_markup=Admin_keyb)
    if call.data.split(":")[1] == "adminid":
        bot.send_message(call.message.chat.id, "Введите telegram id нового администратора", reply_markup=telebot.types.ForceReply())

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
    bot.send_message(message.chat.id, "Админиcтратор успешно добавлен ", reply_markup=Admin_keyb)


print("Ready")
bot.infinity_polling(none_stop=True, interval=0)
