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
            UNIQUE (phone_client),
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
                FOREIGN KEY (category_id) REFERENCES CategoryDish (id),
            );
        """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY (client_id) REFERENCES Clients (id),
                FOREIGN KEY (dish_id) REFERENCES Dish (id),
                FOREIGN KEY (cart_id) REFERENCES ShoppingCart (id),
                date DATETIME,
            );
        """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS ShoppingCart (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY (client_id) REFERENCES Clients (id),
                FOREIGN KEY (dish_id) REFERENCES Dish (id),
                total_price FLOAT,   
            )
        """)

    con.execute("""
                CREATE TABLE IF NOT EXISTS CategoryDish (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    is_stop BOOLEAN,
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
                UNIQUE (phone_number),
                )
            """)


clients = "INSERT OR IGNORE INTO Staff (name, phone_number, delivery_adress) values(?, ?, ?)"
# INSERT OR IGNORE - модификатор для уникальных значений
with con:
    con.execute(clients, ["Артем Наумов", "+375297777777", "ул.Пушкинская д.53"])



with con:
    data = con.execute("SELECT * FROM Clients")
    print(data.fetchall())
    # fetchone