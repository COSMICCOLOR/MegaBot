import sqlite3 as sl

"""
SELECT ('столбцы или * для выбора всех столбцов; обязательно')
FROM ('таблица; обязательно')
WHERE ('условие/фильтрация, например, city = 'Moscow'; необязательно')
GROUP BY ('столбец, по которому хотим сгруппировать данные; необязательно')
HAVING ('условие/фильтрация на уровне сгруппированных данных; необязательно')
ORDER BY ('столбец, по которому хотим отсортировать вывод; необязательно')
"""

con = sl.connect('restaurant1.db')

with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS Clients (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        phone_number TEXT, 
        delivery_adress TEXT, 
        UNIQUE (phone_number)
        );
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS CategoryDish (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            is_stop BOOLEAN
        );
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS Dish (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            photo TEXT,
            price FLOAT,
            time  DATETIME,
            weight FLOAT,
            unit TEXT,
            is_stop BOOLEAN,
            count INTEGER,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES CategoryDish (id)
        );
    """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                dish_id INTEGER,
                cart_id INTEGER,
                date DATETIME,
                FOREIGN KEY (client_id) REFERENCES Clients (id),
                FOREIGN KEY (dish_id) REFERENCES Dish (id),
                FOREIGN KEY (cart_id) REFERENCES ShoppingCart (id)
            );
        """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS ShoppingCart (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                dish_id INTEGER,
                total_price FLOAT,
                FOREIGN KEY (client_id) REFERENCES Clients (id),
                FOREIGN KEY (dish_id) REFERENCES Dish (id)
            )
        """)

    con.execute("""
                CREATE TABLE IF NOT EXISTS BotAdmins (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                phone_number INTEGER,
                position TEXT,
                first_name TEXT,
                last_name TEXT,
                UNIQUE (phone_number)
                );
            """)

# INSERT OR IGNORE - модификатор для уникальных значений
clients = "INSERT OR IGNORE INTO Clients (name, phone_number, delivery_adress) values(?, ?, ?)"
with con:
    con.execute(clients, ["Артем Наумов", "+375297777777", "ул.Пушкинская д.53"])
    con.execute(clients, ["Артем Наумов", "+375297777776", "ул.Пушкинская д.55"])
    con.execute(clients, ["Васіль Быкаў ", "+375291111111", "ул.В.Быкава д.1б кв.1"])

sql_insert = "INSERT OR IGNORE INTO CategoryDish (name, description, is_stop) values(?, ?, ?)"
with con:
    con.execute(sql_insert, ["Беларуская кухня", "Беларуская нацыянальная кухня існуе ўжо шмат стагоддзяў. Прывабнасць традыцыйнай ежы беларусаў заключаецца ў яе садзейнічанні здароваму ладу жыцця, даступнасці, рацыянальнасці спосабаў перапрацоўкі і захоўвання асноўных прадуктаў. Народная кухня – адна з тых этнічных з’яў, якія ўспрымаюцца як нацыянальны здабытак.", False])
    con.execute(sql_insert, ["Японская кухня", "Японская кухня - гэта нацыянальная кухня японцаў, якая адрозніваецца выкарыстаннем натуральных, мінімальна апрацаваных прадуктаў, шырокім выкарыстаннем марскіх прадуктаў, сезоннасцю, характэрнымі стравамі, спецыфічнымі правіламі афармлення страваў, сервіравкай, застольным этыкетам.", False])
    con.execute(sql_insert, ["Итальянская кухня", "Адной з асноўных асаблівасцяў італьянскай кухні з’яўляецца яе прастата, з шматлікімі стравамі, якія складаюцца з некалькіх інгредыентаў, і таму італьянскія кукары часта спадзяюцца на якасць інгредыентаў, а не на складанасць прыгатавання.", False])



with con:
    data = con.execute("SELECT * FROM Clients")
    print(data.fetchall())
    data2 = con.execute("SELECT * FROM CategoryDish")
    print(data2.fetchall())
    # fetchone