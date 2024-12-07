import os
import sqlite3
import csv
from PyQt6.QtSql import *
from PyQt6.QtWidgets import QMessageBox

db_name = 'databases//database.db'


def create_database():
    """Создание базы данных."""
    if os.path.exists(db_name):
        try:
            os.remove(db_name)
        except PermissionError:
            print("Ошибка: файл занят другим процессом. Попробуйте закрыть все соединения с базой данных.")
            return  # Выход из функции, если файл занят
    conn = sqlite3.connect(db_name)
    conn.commit()
    conn.close()


def connect_db(db_name_name):
    """Подключение к базе данных."""
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name_name)
    #db.setConnectOptions("PRAGMA busy_timeout=3000")  # Установите тайм-аут в 3000 мс
    if not db.open():
        print('Не удалось подключиться к базе')
        return False
    return db


def create_order_table():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS Order_table')
        c.execute('''
        CREATE TABLE IF NOT EXISTS Order_table (
        "Сокращенное_имя" TEXT DEFAULT NULL,
        "Сумма_фактического_финансирования" INTEGER DEFAULT NULL
        )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы Order_table: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_table_tp_nir():
    """Создание таблицы Tp_nir."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS Tp_nir')
        c.execute('''
        CREATE TABLE IF NOT EXISTS Tp_nir (
        "Код" INTEGER,
        "Номер" INTEGER,
        "Характер" TEXT,
        "Сокращенное_имя" TEXT DEFAULT NULL,
        "Руководитель" TEXT,
        "Коды_ГРНТИ" TEXT,
        "НИР" TEXT,
        "Должность" TEXT,
        "Плановое_финансирование" INTEGER,
        PRIMARY KEY("Код", "Номер")
        )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы Tp_nir: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_table_vuz():
    """Создание таблицы VUZ."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS VUZ')
        c.execute('''
           CREATE TABLE IF NOT EXISTS VUZ (
           "Код" INTEGER,
           "Наименование" TEXT, 
           "Полное_имя" TEXT, 
           "Сокращенное_имя" TEXT,
           "Регион" TEXT,
           "Город" TEXT,
           "Статус" TEXT,
           "Код_области" INTEGER,
           "Область" TEXT,
           "Тип_уч.заведения" TEXT DEFAULT NULL,
           "Проф" TEXT,
           PRIMARY KEY ("Код")
           )
           ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы VUZ: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_table_grntirub():
    """Создание таблицы grntirub."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS grntirub')
        c.execute('''CREATE TABLE IF NOT EXISTS grntirub (
           "Код_рубрики" INTEGER PRIMARY KEY,
           "Рубрика" TEXT
           )''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы grntirub: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_table_tp_fv():
    """Создание таблицы Tp_fv."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS Tp_fv')
        c.execute('''
           CREATE TABLE IF NOT EXISTS Tp_fv (
           "Код" INTEGER PRIMARY KEY,
           "Сокращенное_имя" TEXT ,
           "Плановое_ финансирование" INTEGER,
           "Фактическое_финансирование" INTEGER ,
           "Количество_НИР" INTEGER)
           ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы Tp_fv: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_table_vuz_summary():
    """Создание таблицы VUZ_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS VUZ_Summary')
        c.execute('''
           CREATE TABLE IF NOT EXISTS VUZ_Summary (
           "Сокращенное_имя" TEXT,
           "Сумма_планового_финансирования" INTEGER,
           "Сумма_количества_НИР" INTEGER,
           "Сумма_фактического_финансирования" INTEGER
           )
           ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы VUZ_Summary: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_table_grnti_summary():
    """Создание таблицы GRNTI_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS GRNTI_Summary')
        c.execute('''
           CREATE TABLE IF NOT EXISTS GRNTI_Summary (
           "Код_рубрики" TEXT,
           "Название_рубрики" TEXT,
           "Количество_НИР" INTEGER,
           "Сумма_планового_финансирования" INTEGER
           )
           ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы GRNTI_Summary: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_table_nir_character_summary():
    """Создание таблицы NIR_Character_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DROP TABLE IF EXISTS NIR_Character_Summary')
        c.execute('''
           CREATE TABLE IF NOT EXISTS NIR_Character_Summary (
           "Характер" TEXT,
           "Количество_НИР" INTEGER,
           "Сумма_планового_финансирования" INTEGER
           )
           ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы NIR_Character_Summary: {e}")
        conn.rollback()
    finally:
        conn.close()


def import_table_tp_nir_from_csv():
    """Импорт таблицы Tp_nir из CSV."""
    csv_file = 'databases//Tp_nir.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        with open(csv_file, mode='r', encoding='cp1251') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)
            row_num = 1
            count = 0
            for row in reader:
                try:
                    c.execute('''INSERT INTO Tp_nir (
                                        "Код", "Номер", "Характер", "Сокращенное_имя", "Руководитель",
                                        "Коды_ГРНТИ", "НИР", "Должность", "Плановое_финансирование"
                                    ) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)
                except sqlite3.IntegrityError as e:
                    count += 1
                row_num += 1
        conn.commit()
    except Exception as e:
        print(f"Ошибка при импорте таблицы Tp_nir: {e}")
        conn.rollback()
    finally:
        conn.close()


def import_table_vuz_from_csv():
    """Импорт таблицы VUZ из CSV."""
    csv_file = 'databases//VUZ.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        with open(csv_file, mode='r', encoding='cp1251') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)
            row_num = 1
            count = 0
            for row in reader:
                try:
                    c.execute('''INSERT INTO VUZ ("Код", "Наименование", "Полное_имя", "Сокращенное_имя",
                                                        "Регион", "Город", "Статус", "Код_области", "Область",
                                                        "Тип_уч.заведения", "Проф")
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''' , row)
                except sqlite3.IntegrityError as e:
                    count += 1
                row_num += 1
        conn.commit()
    except Exception as e:
        print(f"Ошибка при импорте таблицы VUZ: {e}")
        conn.rollback()
    finally:
        conn.close()


def import_table_grntirub_from_csv():
    csv_file = 'databases//grntirub.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        with open(csv_file, mode='r', encoding='cp1251') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)
            row_num = 1
            count = 0
            for row in reader:
                try:
                    c.execute('''INSERT INTO grntirub ("Код_рубрики", "Рубрика")
                                        VALUES (?, ?)''', row)
                except sqlite3.IntegrityError as e:
                    print(f"Error on row {row_num}: {e}")
                    count += 1
                row_num += 1
        conn.commit()
    except Exception as e:
        print(f"Ошибка при импорте таблицы grntirub: {e}")
        conn.rollback()
    finally:
        conn.close()


def import_table_tp_fv_from_csv():
    """Импорт таблицы Tp_fv из CSV."""
    csv_file = 'databases//Tp_fv.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        with open(csv_file, mode='r', encoding='cp1251') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)
            row_num = 1
            count = 0
            for row in reader:
                try:
                    c.execute('''INSERT INTO Tp_fv ("Код", "Сокращенное_имя", "Плановое_финансирование",
                                                        "Фактическое_финансирование", "Количество_НИР")
                                            VALUES (?, ?, ?, ?, ?)''', row)
                except sqlite3.IntegrityError as e:
                    count += 1
                row_num += 1
        conn.commit()
    except Exception as e:
        print(f"Ошибка при импорте таблицы Tp_fv: {e}")
        conn.rollback()
    finally:
        conn.close()


def make_correct_cod_grnti():
    """Создание правильного кода ГРНТИ."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('SELECT "Коды_ГРНТИ" FROM Tp_nir')
        rows = c.fetchall()
        for row in rows:
            cod = row[0]
            if len(cod) == 17:
                cod = cod[:8] + ';' + cod[9:]
            elif 8 <= len(cod) < 17:
                cod = cod[:8] + ';'
            c.execute('UPDATE Tp_nir SET "Коды_ГРНТИ" = ? WHERE "Коды_ГРНТИ" = ?', (cod, row[0]))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при корректировке кодов ГРНТИ: {e}")
        conn.rollback()
    finally:
        conn.close()


def input_short_name_from_vuz():
    """Ввод сокращенного имени из VUZ."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('SELECT VUZ."Код", VUZ."Сокращенное_имя" FROM VUZ INNER JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"')
        rows = c.fetchall()
        for row in rows:
            c.execute('UPDATE Tp_nir SET "Сокращенное_имя" = ? WHERE "Код" = ?', (row[1], row[0]))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при вводе сокращенного имени: {e}")
        conn.rollback()
    finally:
        conn.close()


def fill_tp_fv():
    """Заполнение таблицы Tp_fv."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO Tp_fv ("Код", "Сокращенное_имя", "Плановое_финансирование", "Фактическое_финансирование", "Количество_НИР")
                    SELECT 
                        VUZ."Код",
                        VUZ."Сокращенное_имя",
                        SUM (Tp_nir."Плановое_финансирование"),
                        0, 
                        COUNT(Tp_nir."Номер")
                    FROM VUZ
                    INNER JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
                    GROUP BY 
                        VUZ."Код", 
                        VUZ."Сокращенное_имя"
                    ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при заполнении таблицы Tp_fv: {e}")
        conn.rollback()
    finally:
        conn.close()


def fill_vuz_summary():
    """Заполнение таблицы VUZ_Summary только для вузов, которые есть в Tp_nir."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM VUZ_Summary')
        query = '''
            INSERT INTO VUZ_Summary ("Сокращенное_имя", "Сумма_планового_финансирования", "Сумма_количества_НИР", "Сумма_фактического_финансирования")
            SELECT 
                VUZ."Сокращенное_имя",
                SUM(Tp_nir."Плановое_финансирование") AS "Сумма_планового_финансирования",
                COUNT(Tp_nir."Номер") AS "Сумма_количества_НИР",
                SUM(Tp_fv."Фактическое_финансирование") AS "Сумма_фактического_финансирования"
            FROM VUZ
            LEFT JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
            LEFT JOIN Tp_fv ON VUZ."Код" = Tp_fv."Код"
            WHERE Tp_nir."Код" IS NOT NULL 
            GROUP BY VUZ."Сокращенное_имя"
        '''
        c.execute(query)

        # Добавляем итоговую строку
        c.execute('''
            INSERT INTO VUZ_Summary ("Сокращенное_имя", "Сумма_планового_финансирования", "Сумма_количества_НИР", "Сумма_фактического_финансирования")
            SELECT 
                'ИТОГО',
                SUM("Сумма_планового_финансирования"),
                SUM("Сумма_количества_НИР"),
                SUM("Сумма_фактического_финансирования")
            FROM VUZ_Summary
        ''')
        conn.commit()
    except Exception as e:
        print(f"Ошибка при заполнении таблицы VUZ_Summary: {e}")
        conn.rollback()
    finally:
        conn.close()


def fill_grnti_summary():
    """Заполнение таблицы GRNTI_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM GRNTI_Summary')  # Очистка таблицы перед заполнением
        query = '''
            INSERT INTO GRNTI_Summary ("Код_рубрики", "Название_рубрики", "Количество_НИР", "Сумма_планового_финансирования")
            SELECT 
                substr(Tp_nir."Коды_ГРНТИ", 1, 2) AS "Код_рубрики",  -- Первые две цифры из Коды_ГРНТИ
                grntirub."Рубрика" AS "Название_рубрики",
                COUNT(Tp_nir."Номер") AS "Количество_НИР",  -- Количество НИР по рубрике
                SUM(Tp_nir."Плановое_финансирование") AS "Сумма_планового_финансирования"  -- Сумма планового финансирования
            FROM Tp_nir
            INNER JOIN grntirub ON substr(Tp_nir."Коды_ГРНТИ", 1, 2) = grntirub."Код_рубрики"
            GROUP BY 
                substr(Tp_nir."Коды_ГРНТИ", 1, 2),
                grntirub."Рубрика"
        '''
        c.execute(query)
        conn.commit()
    except Exception as e:
        print(f"Ошибка при заполнении таблицы GRNTI_Summary: {e}")
        conn.rollback()
    finally:
        conn.close()


def fill_nir_character_summary():
    """Заполнение таблицы NIR_Character_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM NIR_Character_Summary')  # Очистка таблицы перед заполнением

        query = '''
            INSERT INTO NIR_Character_Summary ("Характер", "Количество_НИР", "Сумма_планового_финансирования")
            SELECT 
                "Характер",
                COUNT("Номер") AS "Количество_НИР",
                SUM("Плановое_финансирование") AS "Сумма_планового_финансирования"
            FROM Tp_nir
            GROUP BY "Характер"
        '''
        c.execute(query)

        # Добавляем итоговую строку
        c.execute('''
            INSERT INTO NIR_Character_Summary ("Характер", "Количество_НИР", "Сумма_планового_финансирования")
            SELECT 
                'ИТОГО',
                SUM("Количество_НИР"),
                SUM("Сумма_планового_финансирования")
            FROM NIR_Character_Summary
        ''')

        conn.commit()  # Подтверждаем транзакцию
    except Exception as e:
        print(f"Ошибка при заполнении NIR_Character_Summary: {e}")
        conn.rollback()  # Откат транзакции в случае ошибки
    finally:
        conn.close()  # Закрываем соединение


def grnti_to_cmb():
    connection = sqlite3.connect('databases//database.db')
    cursor = connection.cursor()

    cursor.execute("SELECT Код_рубрики, Рубрика FROM grntirub")
    codes_and_names = cursor.fetchall()  # Получаем все записи в виде списка кортежей

    connection.close()

    grnti_to = [f'{str(cod).zfill(2)} - {name}' for cod, name in codes_and_names]
    return grnti_to



def prepare_tables():
    """Подготовка таблиц."""
    create_database()

    create_table_tp_nir()
    create_table_vuz()
    create_table_grntirub()
    create_table_tp_fv()
    create_table_vuz_summary()
    create_table_grnti_summary()
    create_table_nir_character_summary()
    create_order_table()

    import_table_tp_nir_from_csv()
    import_table_vuz_from_csv()
    import_table_grntirub_from_csv()
    import_table_tp_fv_from_csv()

    make_correct_cod_grnti()
    input_short_name_from_vuz()
    fill_tp_fv()

    fill_vuz_summary()
    fill_grnti_summary()
    fill_nir_character_summary()

# prepare_tables()