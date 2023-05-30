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
token = '5937676517:AAEG8U11wayyFFQmbJKi3Y3BdINCzUTIDWs'
bot = telebot.TeleBot(token)
conn = sqlite3.connect('restaurant1.db', check_same_thread=False)
markdown = """
    *bold text*
    _italic text_
    [text](URL)
    """

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
    global client_id
    clients_telegram_id = [i[4] for i in conn.execute(f"SELECT * FROM Clients")]
    print("айди телеги юзеров", clients_telegram_id)

# with conn:
#     admin = "SELECT * FROM BotAdmins"
#     cursor.execute(admin)
#     conn.commit()
#     results = cursor.fetchall()
#     print(admin)


with conn:
    orders_telegram_id = [i[5] for i in conn.execute(f"SELECT * FROM Orders")]
    orders_datetime = [i[4] for i in conn.execute(f"SELECT * FROM Orders")]
    #print(type(orders_telegram_id[0]), orders_telegram_id)

with conn:
    data = conn.execute("SELECT * FROM Dish")
    #print(data.fetchall())
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Dish")
    data2 = cursor.fetchall()  # fetchone
    dish_names = [i[1] for i in conn.execute(f"SELECT * FROM Dish")]
    dish_cat_ids = [str(i[11]) for i in conn.execute(f"SELECT * FROM Dish")]
    dish_ids = [str(i[0]) for i in conn.execute(f"SELECT * FROM Dish")]
    dish_dict2 = dict(zip(dish_names, dish_ids))
    dish_dict = dict(zip(dish_names, dish_cat_ids))
    dish_all_dict = dict(zip(dish_names, [[i[1],i[2], i[3], i[4],i[5], i[6], i[7], i[9], i[0]] for i in conn.execute(f"SELECT * FROM Dish")]))


# print(dish_names)
# print(dish_dict)

with conn:
    data = conn.execute("SELECT * FROM Reviews")
    #print(data.fetchall())
    review_order = [i[1] for i in conn.execute(f"SELECT * FROM Reviews")]
    review_dish = [i[2] for i in conn.execute(f"SELECT * FROM Reviews")]
    client_id = [i[3] for i in conn.execute(f"SELECT * FROM Reviews")]
    orders_id = [i[4] for i in conn.execute(f"SELECT * FROM Reviews")]
   # print("qqqqqqqqq", review_order, client_id)
    dish_id = [str(i[5]) for i in conn.execute(f"SELECT * FROM Reviews")]
    review_order_dict = dict(zip(review_order[-3:-1], client_id[-3:-1]))  # можно корректировать индексами количество выводимых отзывов
    #print(review_order_dict)
    review_dish_dict = dict(zip(dish_id, review_dish))
    #print(review_dish_dict)
    client_name = [i[1] for i in conn.execute(f"SELECT * FROM Clients")]
    client_id2 = [i[0] for i in conn.execute(f"SELECT * FROM Clients")]
    client_dict = dict(zip(client_id2, client_name))
    #print(client_dict)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Reviews")
    data_feedback = cursor.fetchall()  # fetchone
    feedback = [i[1] for i in conn.execute(f"SELECT * FROM Reviews")]
    cursor.execute("SELECT * FROM Clients WHERE id = 4")
    gg = cursor.fetchall()
    #print(gg)

# Создаем клавиатуру и кнопки для главного меню USER-панели
Main_inline_keyb = InlineKeyboardMarkup()
Main_inline_keyb.add(InlineKeyboardButton("Меню ресторана", callback_data="menu:txt1"))
Main_inline_keyb.add(InlineKeyboardButton("Моя корзина", callback_data="menu:txt3"))
Main_inline_keyb.add(InlineKeyboardButton("Мои заказы", callback_data="menu:txt4"))
Main_inline_keyb.add(InlineKeyboardButton("О нас", callback_data="menu:txt2"))
Main_inline_keyb.add(InlineKeyboardButton("Профиль пользователя", callback_data="menu:profile"))


"""***START Функция для создания клавиатуры с обновляемой кнопкой количества заказываемого блюда START***"""
count = 1  # переменная для хранения количества добавляемого в корзину блюда
def create_keyboard():  # функция для создания клавиатуры под карточкой блюда
    markup_dish = InlineKeyboardMarkup(row_width=3)
    markup_dish.add(InlineKeyboardButton('-', callback_data='1:minus'),
                    InlineKeyboardButton(str(count), callback_data=':count'),
                    InlineKeyboardButton('+', callback_data='2:plus'),
                    InlineKeyboardButton("В корзину", callback_data="0:basket"),
                    InlineKeyboardButton('Заказать', callback_data='3:buy'))
    return markup_dish
"""***END Функция для создания клавиатуры с обновляемой кнопкой количества заказываемого блюда END***"""


# Создаем клавиатуру и кнопки для главного меню и АДМИН-панели
admin_keyb = InlineKeyboardMarkup()
admin_keyb.add(InlineKeyboardButton("Добавление администратора➕", callback_data="admin:addadmin"))
admin_keyb.add(InlineKeyboardButton("Удаление администратора➖", callback_data="admin:deladmin"))
admin_keyb.add(InlineKeyboardButton("Редактирование администратора🛠️", callback_data="admin:redadmin"))

@bot.message_handler(content_types=['text'])
def start(message) :
    if message.text.lower() == '/start':
        bot.send_message(message.chat.id,
                         '''Добро пожаловать в чат-бот "FoodBot". Здесь Вы можете заказать еду по вкусу из ресторана "Літвіны".\nЧто Вас интересует?''',
                         reply_markup=Main_inline_keyb)

    if message.text.lower() == '/addadmin':
        # user_id = message.from_user.id  # id телеги пользователя
        # print(user_id)
        # with conn:
        #     row = [i[1] for i in conn.execute("SELECT * FROM BotAdmins")]
        #
        # if user_id not in row :  # проверяем id на пригодность
        #     bot.send_message(message.chat.id, "Вы не являетесь администратором.\nВыберите лучше покушать\U0001F609 ", reply_markup=Main_inline_keyb)
        # else :  # если есть, то показываем админу клаву для управления админкой
            bot.send_message(message.chat.id, '''Добро пожаловать в админ-панель "FoodBot". Здесь Вы можете изменить меню и просмотреть отзывы ресторана "Літвіны"''', reply_markup=admin_keyb)
    global user_telegram_id
    user_telegram_id = message.from_user.id
    print(type(user_telegram_id), message.from_user.id)


# @bot.callback_query_handler(func=lambda call : call.data.split(":"))
# def query_handler(call) :
#     bot.answer_callback_query(callback_query_id=call.id)
#     if call.data.split(':')[1] == "txt1" :

@bot.callback_query_handler(func=lambda call: call.data.split(":"))
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id,)
    if call.data.split(':')[1] == "txt1":
       # print("главные категории")
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
       # print("субкатегории")
       # print(call.data.split(':')[0], call.data.split(':')[1])
        # Создаем клавиатуру и кнопки для субкатегорий (напр., "Суши и роллы")
        global Sub_inline_keyb
        Sub_inline_keyb = InlineKeyboardMarkup()
        [Sub_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in subcat_dict3.items() if str(value[0]) == call.data.split(':')[1]]
        Sub_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        Sub_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:b2"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Sub_inline_keyb)
    if call.data.split(':')[0] in subcat_dict3:
      #  print("виды однородных блюд типа супы, пиццы и тд")
        #print(call.data.split(':')[0], call.data.split(':')[1][1:], call.data.split(':'))
        # Создаем клавиатуру и кнопки для конкретных блюд внутри субкатегорий (напр., "Филадельфия маки")
        Dish_inline_keyb = InlineKeyboardMarkup()
        [Dish_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"{key}:{value}")) for key, value in dish_dict.items() if value == call.data.split(':')[1][1:]]
        Dish_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        Dish_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:b3"))
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=Dish_inline_keyb)

    # if call.data.split(':')[0] in dish_dict:
    #     print(call.data.split(':')[0])
    #     markup_dish = InlineKeyboardMarkup(row_width=3)
    #     markup_dish.add(InlineKeyboardButton('<', callback_data='left'),
    #                     InlineKeyboardButton('Кол-во', callback_data='None'),
    #                     InlineKeyboardButton('>', callback_data='right'),
    #                     InlineKeyboardButton('Заказать', callback_data='buy'),
    #                     InlineKeyboardButton("В корзину", callback_data="basket"),)
    #     if call.data.split(':')[0] in dish_all_dict:
    #         # img = open(rf"C:\Users\admin\MegaBot\photo\{dish_all_dict[call.data.split(':')[0]][2]}", 'rb')
    #         # bot.send_photo(call.message.chat.id, img)
    #         bot.send_message(call.message.chat.id,
    #                          f"{call.data.split(':')[0]}\nОписание:{dish_all_dict[call.data.split(':')[0]][1]}\nЦена: {dish_all_dict[call.data.split(':')[0]][3]}BYN (В упаковке вы увидите  {dish_all_dict[call.data.split(':')[0]][7]}шт.)\nВес:"
    #                          f" {dish_all_dict[call.data.split(':')[0]][5]}"
    #                          f" {dish_all_dict[call.data.split(':')[0]][6]}\nВремя "
    #                          f"приготовления: {dish_all_dict[call.data.split(':')[0]][4]} миунут!\n",
    #                          reply_markup=markup_dish)

#START________________________________code serezha

    global dish_ids
    global dish_names

    if call.data.split(':')[0] in dish_dict:
        dish_ids = []
        # markup_dish = InlineKeyboardMarkup(row_width=3)
        # markup_dish.add(InlineKeyboardButton('-', callback_data='1:minus'),
        #                 InlineKeyboardButton(str(count), callback_data='count'),
        #                 InlineKeyboardButton('+', callback_data='2:plus'),
        #                 InlineKeyboardButton("В корзину", callback_data="0:basket"),
        #                 InlineKeyboardButton('Заказать', callback_data='3:buy'))
    if call.data.split(':')[0] in dish_all_dict:
        #print("yyyyyyyyyyyy", call.data.split(':'), dish_all_dict[call.data.split(':')[0]][2])
        # img = open(rf"C:\Users\admin\MegaBot\photo\{dish_all_dict[call.data.split(':')[0]][2]}", 'rb')
        # bot.send_photo(call.message.chat.id, img)
        dish_ids.append(dish_all_dict[call.data.split(':')[0]][8])
        dish_names = dish_all_dict[call.data.split(':')[0]][0]
        global result_dish  # формируем карточку блюда и отправляем юзеру с клавиатурой для заказа и добавления в корзину
        result_dish = f"{call.data.split(':')[0]}\n" \
                      f"Описание:{dish_all_dict[call.data.split(':')[0]][1]}\n" \
                      f"Цена: {dish_all_dict[call.data.split(':')[0]][3]}BYN (В упаковке вы увидите  {dish_all_dict[call.data.split(':')[0]][7]}шт.)\n" \
                      f"Вес:{dish_all_dict[call.data.split(':')[0]][5]}{dish_all_dict[call.data.split(':')[0]][6]}\n" \
                      f"Время приготовления: {dish_all_dict[call.data.split(':')[0]][4]} миунут!\n"
        with open("photo/" + dish_all_dict[call.data.split(':')[0]][2], "rb") as img:  # calldata - id блюда и название соотв-й картинки этого блюда
            bot.send_photo(call.message.chat.id, photo=img)
        bot.send_message(call.message.chat.id, f"{result_dish}", reply_markup=create_keyboard())

    """***START Обработки колбэка от клавиатуры с обновляемой кнопкой количества заказываемого блюда START***"""
    global count  # используем глобальную переменную для количества добавляемого в корзину блюда
    bot.answer_callback_query(call.id)  # подтверждаем нажатие
    if call.data.split(':')[1] == "minus":  # если нажата кнопка "-"
        if count > 1:  # если количество больше одного
            count -= 1  # уменьшаем количество на один
            bot.edit_message_text(f"{result_dish}", call.message.chat.id, call.message.message_id,
                                  reply_markup=create_keyboard())  # обновляем сообщение с клавиатурой
    elif call.data.split(':')[1] == "plus":  # если нажата кнопка "+"
        count += 1  # увеличиваем количество на один
        bot.edit_message_text(f"{result_dish}", call.message.chat.id, call.message.message_id,
                              reply_markup=create_keyboard())  # обновляем сообщение с клавиатурой
    """***END Обработки колбэка от клавиатуры с обновляемой кнопкой количества заказываемого блюда END***"""

    global dict_info_dish_id
    client_id = int(call.message.chat.id)
    if call.data.split(':')[1] == 'basket':
        dict_info_dish_id = int(dish_ids[0])
        #print(dict_info_dish_id, type(dict_info_dish_id))
        cart = "INSERT OR IGNORE INTO ShoppingCart (client_id, dish_id, total_price) values(?, ?, ?)"
        with conn:
            conn.execute(cart, [client_id, dict_info_dish_id, 5.0])
        conn.commit()

    if call.data.split(':')[1] == 'buy':
        sravnenie_ids = [i[0] for i in cursor.execute(
            f'SELECT ShoppingCart.dish_id FROM ShoppingCart WHERE ShoppingCart.client_id = {client_id}')]
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
                result += f'Блюдо: {j[1]}\n'
        bot.send_message(call.message.chat.id, f'{result} Цена:{total_price}')
# END_______________________________________________________________________________________________code serezha
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
        bot.send_message(call.message.chat.id, f"{result_card}", reply_markup=AfterReview_inline_keyb)
    # if call.data.split(':')[1] == "r2":
    #     # Создаем клавиатуру и кнопки для блюд с отзывами
    #     global ReviewDish_inline_keyb
    #     ReviewDish_inline_keyb = InlineKeyboardMarkup()
    #     [ReviewDish_inline_keyb.add(InlineKeyboardButton(key, callback_data=f"r{key}:{value}r")) for key, value in
    #      dish_dict2.items() if value in dish_id]
    #     ReviewDish_inline_keyb.add(InlineKeyboardButton("Оставить отзыв", callback_data="feedback:r3"))
    #     ReviewDish_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
    #     ReviewDish_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:txt2"))
    #     bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=ReviewDish_inline_keyb)
    # print(call.data.split(':'))
    # if call.data.split(':')[1][:-1] in review_dish_dict:  # callback от клавиатуры и кнопок ReviewDish_inline_keyb - блюда с отзывами, напр.: ["rДеруны", "7r"], где 7 - это id блюда
    #     result_card = ""
    #     for key, value in review_dish_dict.items():
    #         if key == call.data.split(':')[1][:-1]:
    #             result_card += f"\U0001F5E8{review_dish_dict[call.data.split(':')[1][:-1]]}\n"
    #     AfterReviewDish_inline_keyb = InlineKeyboardMarkup()
    #     AfterReviewDish_inline_keyb.add(InlineKeyboardButton("Оставить отзыв", callback_data="feedback:r3"))
    #     AfterReviewDish_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
    #     AfterReviewDish_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="review:r2"))
    #     with open("photo/" + call.data.split(':')[1][:-1] + ".jpg", "rb") as img:  # calldata - id блюда и название соотв-й картинки этого блюда
    #         bot.send_photo(call.message.chat.id, photo=img)
    #     bot.send_message(call.message.chat.id, f"{result_card}", reply_markup=AfterReviewDish_inline_keyb)
    if call.data.split(':')[1] == "r3":
        MakeReviewError_inline_keyb = InlineKeyboardMarkup()
        MakeReviewError_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
        MakeReviewError_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:txt2"))
        # MakeReviewSuccess_inline_keyb = InlineKeyboardMarkup()
        # MakeReviewSuccess_inline_keyb.add(InlineKeyboardButton("Отзыв на заказ", callback_data="feedback:r4"))
        # MakeReviewSuccess_inline_keyb.add(InlineKeyboardButton("Отзыв на блюдо", callback_data="feedback:r5"))
        if user_telegram_id in orders_telegram_id:
            print("clients id telegram", user_telegram_id)
            #кнопка оставить отзыв на заказ
            #кнопка оставить отзыв на блюдо
            # bot.send_message(call.message.chat.id, "Выбрать:", reply_markup=MakeReviewSuccess_inline_keyb)
            bot.answer_callback_query(call.id)  # подтвердить нажатие
            bot.send_message(call.message.chat.id, "Как вы оцениваете работу ресторана?", reply_markup=telebot.types.ForceReply())  # спрашиваем пользователя о его отзыве
        else:
            bot.send_message(call.message.chat.id, "Оставить отзыв о работе ресторана Вы сможете после оформления заказа с помощью нашаего чат-бота. Спасибо!",
                             reply_markup=MakeReviewError_inline_keyb)  # выдать клаву если пользователь ранее не делал заказов
    # if call.data.split(':')[1] == "r4":
    #     ClientOrders_inline_keyb = InlineKeyboardMarkup()
    #     [ClientOrders_inline_keyb.add(InlineKeyboardButton(date_info, callback_data=f"{date_info}")) for date_info in orders_datetime]
    #     ClientOrders_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu:b1"))
    #     ClientOrders_inline_keyb.add(InlineKeyboardButton("Назад", callback_data="menu:txt2"))
    #     bot.send_message(call.message.chat.id, "Вот все Ваши заказы. Выберите тот, на который хотите оставить отзыв:", reply_markup=ClientOrders_inline_keyb)
    global addm_adminname, addm_adminlast, addm_adminphone, addm_adminpos
    addm_adminname = "Имя"
    addm_adminlast = "Фамилия"
    addm_adminphone = "Номер телефона"
    addm_adminpos= "Должность"
    if call.data.split(':')[1] == "addadmin": #клава для добавления админа
        add_inline_keyb = InlineKeyboardMarkup()
        add_inline_keyb.add(InlineKeyboardButton("Имя💎", callback_data="addm:adminname"))
        add_inline_keyb.add(InlineKeyboardButton("Фамилия👑", callback_data="addm:adminlast"))
        add_inline_keyb.add(InlineKeyboardButton("Номер телефона📱", callback_data="addm:adminphone"))
        add_inline_keyb.add(InlineKeyboardButton("Должность🤵", callback_data="addm:adminpos"))
        add_inline_keyb.add(InlineKeyboardButton("Сохранить\u2705", callback_data="addm:adminsave"))
        add_inline_keyb.add(InlineKeyboardButton("Вернуться назад↩ ", callback_data="addm:backmenu"))
        bot.send_message(call.message.chat.id, "Добавьте данные о новом администраторе", reply_markup=add_inline_keyb)
    if call.data.split(':')[1] == "backmenu" :
        bot.send_message(call.message.chat.id, "Добавьте данные о новом администраторе", reply_markup=admin_keyb)
    #
    # if addm_adminname != "Указать имя" and addm_adminlast != "Указать Фамилию" and len(addm_adminphone) == 13 and addm_adminpos != "Должность":
    #     Success_reg_inline_keyb = InlineKeyboardMarkup()
    #     Success_reg_inline_keyb.add(InlineKeyboardButton("Вернуться в меню", callback_data="add_inline_keyb"))
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, f"Вы успешно прошли регистрацию.\n"
    #                                            f"Ваш профиль:\n"
    #                                            f"Имя: {addm_adminname}\n"
    #                                            f"Фамилия: {addm_adminlast}\n"
    #                                            f"Телефон: {addm_adminphone}\n"
    #                                            f"Должность: {addm_adminpos}\n\n",
    #                      reply_markup=admin_keyb)










# обработка ответа пользователя на вопрос о его отзыве на работу ресторана с последующей запись в БД
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text == "Как вы оцениваете работу ресторана?")
def handle_review_answer(message):
    client_id = [i[0] for i in conn.execute(f"SELECT id FROM Clients WHERE telegram_id = {user_telegram_id}")][0]
    orders_id = [i[0] for i in conn.execute(f"SELECT id FROM Orders WHERE telegram_id = {user_telegram_id}")][-1] # id последнего заказа из БД
    print("айди юзера", client_id, "id последнего заказа из БД", orders_id)
    dish_id = None
    review_order = message.text  # текст отзыва пользователя
    review_dish = ""
    with conn:
        conn.execute("INSERT INTO Reviews (review_order, review_dish, client_id, orders_id, dish_id) VALUES (?, ?, ?, ?, ?)",
                     (review_order, review_dish, client_id, orders_id, dish_id)) # добавьте новую запись в таблицу "Отзывы"
    conn.commit()  # сохраняем изменения в базе данных
    bot.send_message(message.chat.id, "Спасибо за Ваш отзыв!", reply_markup=Main_inline_keyb)






print("Ready")
bot.infinity_polling(none_stop=True, interval=0)