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
        CREATE TABLE IF NOT EXISTS Staff (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            birthday DATETIME,
            phone_number TEXT,
            position TEXT,
            position_id INTEGER,
            FOREIGN KEY (position_id) REFERENCES Positions (id),
            UNIQUE(phone_number)
        );
    """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS Positions (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                salary INTEGER,
                office INTEGER
            );
        """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS Services (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                position TEXT,
                price TEXT,
                date DATETIME,
                position_id INTEGER,
                FOREIGN KEY (position_id) REFERENCES Positions (id)
            );
        """)

    con.execute("""
            CREATE TABLE IF NOT EXISTS Clients (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                last_name TEXT,
                first_name TEXT,
                middle_name TEXT,
                birthday DATETIME,
                phone_number TEXT,
                file BINARY,
                UNIQUE(phone_number)
            );
        """)

    con.execute("""
                CREATE TABLE IF NOT EXISTS Orders (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    service_id INTEGER,
                    staff_id INTEGER,
                    service_start DATETIME,
                    service_end DATETIME,
                    FOREIGN KEY (client_id) REFERENCES Clients (id),
                    FOREIGN KEY (service_id) REFERENCES Services (id),
                    FOREIGN KEY (staff_id) REFERENCES Staff (id)
                );
            """)


sql_insert = "INSERT OR IGNORE INTO Staff (last_name, first_name, middle_name, birthday, phone_number, position, position_id) values(?, ?, ?, ?, ?, ?, ?)"
# INSERT OR IGNORE - модификатор для уникальных значений
with con:
    con.execute(sql_insert, ["фамилия", "имя", "отчество", '2005-01-13', "+375297777777", "терапевт", 1])
    # executemany - для двумерного
    con.execute(sql_insert, ["фамилия2", "имя2", "отчество2", '2005-01-14', "+375297777778", "стоматолог", 2])

sql_insert = "INSERT OR IGNORE INTO Positions (name, salary, office) values(?, ?, ?)"
# INSERT OR IGNORE - модификатор для уникальных значений
with con:
    con.execute(sql_insert, ["терапевт", 1000, 10])
    # executemany - для двумерного
    con.execute(sql_insert, ["стоматолог", 2000, 11])

sql_insert = "INSERT OR IGNORE INTO Services (service_name, position, price, date, position_id) values(?, ?, ?, ?, ?)"
# INSERT OR IGNORE - модификатор для уникальных значений
with con:
    con.execute(sql_insert, ["консультация", "терапевт", 50, '2023-03-31', 1])
    # executemany - для двумерного
    con.execute(sql_insert, ["лечение", "стоматолог", 100, '2023-03-14', 2])

sql_insert = "INSERT OR IGNORE INTO Clients (last_name, first_name, middle_name, birthday, phone_number, file) values(?, ?, ?, ?, ?, ?)"
# INSERT OR IGNORE - модификатор для уникальных значений
with con:
    con.execute(sql_insert, ["клиент1", "имя", "отчество", '1955-01-13', "+375297777755", "JSON"])
    # executemany - для двумерного
    con.execute(sql_insert, ["клиент2", "имя2", "отчество2", '2000-01-14', "+375297777744", "JSON"])

sql_insert = "INSERT OR IGNORE INTO Orders (client_id, service_id, staff_id, service_start, service_end) values(?, ?, ?, ?, ?)"
# INSERT OR IGNORE - модификатор для уникальных значений
with con:
    con.execute(sql_insert, [1, 1, 1, '2023-03-31 10:00:00', "2022-12-05 11:00:00"])
    # executemany - для двумерного
    con.execute(sql_insert, [2, 2, 2, '2023-03-31 11:00:00', "2023-03-31 12:00:00"])

with con:
    data = con.execute("SELECT * FROM Staff")
    print(data)
    print(data.fetchall())
    # fetchone