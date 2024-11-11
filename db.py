import os
import sqlite3
import csv
from PyQt6.QtSql import *
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QTextEdit
from PyQt6.QtCore import Qt


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
    if not db.open():
        print('Не удалось подключиться к базе')
        return False
    return db


def create_table_tp_nir():
    """Создание таблицы Tp_nir."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
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
    conn.close()

def create_table_vuz():
    """Создание таблицы VUZ."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
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
    conn.close()


def create_table_grntirub():
    """Создание таблицы grntir ub."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS grntirub')
    c.execute('''CREATE TABLE IF NOT EXISTS grntirub (
       "Код_рубрики" INTEGER PRIMARY KEY,
       "Рубрика" TEXT
       )''')

    conn.commit()
    conn.close()


def create_table_tp_fv():
    """Создание таблицы Tp_fv."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS Tp_fv')
    c.execute('''
       CREATE TABLE IF NOT EXISTS Tp_fv (
       "Код" INTEGER PRIMARY KEY,
       "Сокращенное_имя" TEXT ,
       "Плановое_финансирование" INTEGER,
       "Фактическое_финансирование" INTEGER ,
       "Количество_НИР" INTEGER)
       ''')

    conn.commit()
    conn.close()

def create_table_vuz_summary():
    """Создание таблицы VUZ_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
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
    conn.close()

def create_table_grnti_summary():
    """Создание таблицы GRNTI_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
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
    conn.close()

def create_table_nir_character_summary():
    """Создание таблицы NIR_Character_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS NIR_Character_Summary')
    c.execute('''
       CREATE TABLE IF NOT EXISTS NIR_Character_Summary (
       "Характер" TEXT,
       "Количество_НИР" INTEGER,
       "Сумма_планового_финансирования" INTEGER
       )
       ''')
    conn.commit()
    conn.close()

def import_table_tp_nir_from_csv():
    """Импорт таблицы Tp_nir из CSV."""
    csv_file = 'databases//Tp_nir.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    with open(csv_file, mode='r', encoding='cp1251') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        row_num = 1
        count = 0
        for row in reader:
            try:
                c.execute('''INSERT  INTO Tp_nir (
                                        "Код", "Номер", "Характер", "Сокращенное_имя", "Руководитель",
                                        "Коды_ГРНТИ", "НИР", "Должность", "Плановое_финансирование"
                                    ) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)
            except sqlite3.IntegrityError as e:
                print(f"Error on row {row_num}: {e}")
                count += 1
            row_num += 1

    print(f"Total errors: {count}")
    conn.commit()
    conn.close()


def import_table_vuz_from_csv():
    """Импорт таблицы VUZ из CSV."""
    csv_file = 'databases//VUZ.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    with open(csv_file, mode='r', encoding='cp1251') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        row_num = 1
        count = 0
        for row in reader:
            try:
                c.execute('''INSERT  INTO VUZ ("Код", "Наименование" , "Полное_имя", "Сокращенное_имя",
                                                        "Регион", "Город", "Статус", "Код_области", "Область",
                                                        "Тип_уч.заведения","Проф")
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)
            except sqlite3.IntegrityError as e:
                print(f"Error on row {row_num}: {e}")
                count += 1
            row_num += 1

    print(f"Total errors: {count}")
    conn.commit()
    conn.close()


def import_table_grntirub_from_csv():
    """Импорт таблицы grntirub из CSV."""
    csv_file = 'databases//grntirub.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    with open(csv_file, mode='r', encoding='cp1251') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        row_num = 1
        count = 0
        for row in reader:
            try:
                c.execute('''INSERT  INTO grntirub ("Код_рубрики" ,"Рубрика")
                                        VALUES (?, ?)''', row)
            except sqlite3.IntegrityError as e:
                print(f"Error on row {row_num}: {e}")
                count += 1
            row_num += 1

    print(f"Total errors: {count}")
    conn.commit()
    conn.close()


def import_table_tp_fv_from_csv():
    """Импорт таблицы Tp_fv из CSV."""
    csv_file = 'databases//Tp_fv.csv'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    with open(csv_file, mode='r', encoding='cp1251') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        row_num = 1
        count = 0
        for row in reader:
            try:
                c.execute('''INSERT  INTO Tp_fv ("Код", "Сокращенное_имя", "Плановое_финансирование",
                                                        "Фактическое_финансирование", "Количество_НИР")
                                            VALUES (?, ?, ?, ?, ?)''', row)
            except sqlite3.IntegrityError as e:
                print(f"Error on row {row_num}: {e}")
                count += 1
            row_num += 1

    print(f"Total errors: {count}")
    conn.commit()
    conn.close()


def make_correct_cod_grnti():
    """Создание правильного кода ГРНТИ."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''SELECT 
    "Коды_ГРНТИ" AS cods
    FROM Tp_nir''')
    rows = c.fetchall()
    for row in rows:
        cod = row[0]
        if len(cod) == 17:
            cod = cod[:8] + ';' + cod[9:]
        elif 8 <= len(cod) < 17:
            cod = cod[:8] + ';'

        c.execute('''UPDATE Tp_nir
                     SET "Коды_ГРНТИ" = ?
                      WHERE "Коды_ГРНТИ" = ?''',(cod, row[0]))
    conn.commit()
    conn.close()


def input_short_name_from_vuz():
    """Ввод сокращенного имени из VUZ."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''SELECT VUZ."Код",
                 VUZ."Сокращенное_имя"
                 FROM VUZ
                 INNER JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код" ''')
    rows = c.fetchall()
    for row in rows:
        c.execute('''UPDATE Tp_nir
                     SET "Сокращенное_имя" = ?
                      WHERE "Код" = ?''',(row[1], row[0]))
    conn.commit()
    conn.close()


def fill_tp_fv():
    """Заполнение таблицы Tp_fv."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''INSERT INTO Tp_fv ("Код", "Сокращенное_имя", "Плановое_финансирование", "Количество_НИР")
                SELECT 
                    VUZ."Код",
                    VUZ."Сокращенное_имя",
                    SUM(Tp_nir."Плановое_финансирование"),
                    COUNT(Tp_nir."Номер")
                FROM VUZ
                INNER JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
                GROUP BY 
                    VUZ."Код", 
                    VUZ."Сокращенное_имя"
                ''')
    conn.commit()
    conn.close()

def fill_vuz_summary():
    """Заполнение таблицы VUZ_Summary только для вузов, которые есть в Tp_nir."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

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
    conn.close()

def fill_grnti_summary():
    """Заполнение таблицы GRNTI_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

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
    conn.close()

def fill_nir_character_summary():
    """Заполнение таблицы NIR_Character_Summary."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

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

    conn.commit()
    conn.close()

def connect_db(db_name):
    """Подключение к базе данных."""
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print('Не удалось подключиться к базе')
        return False
    return db


def get_column_values_from_table(column_name):
    """Получение значений столбца из таблицы."""
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        query = f"SELECT {column_name} FROM Tp_nir INNER JOIN VUZ ON VUZ.Код = Tp_nir.Код"
        c.execute(query)
        column = c.fetchall()
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()
    return column


def get_column_name_with_linked_value(value):
    """Получение имени столбца с выбранным значением."""
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("PRAGMA table_info(Tp_nir)")
        rows1 = c.fetchall()
        c.execute("PRAGMA table_info(VUZ)")
        rows2 = c.fetchall()
        rows = rows1 + rows2

        for row in rows:
            column_name = row[1]  # Имя столбца
            query = f"SELECT {column_name} FROM Tp_nir INNER JOIN VUZ ON VUZ.Код = Tp_nir.Код WHERE {column_name} = ?"
            c.execute(query, (value,))
            if c.fetchone():
                return column_name
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def hard_filter(self, selected_values):
    """Фильтрация по выбранным значениям."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    previous_results = None
    for selected_value in selected_values:
        column_name = get_column_name_with_linked_value(selected_value)

        if previous_results is None:
            query = '''
                SELECT *
                FROM Tp_fv
                INNER JOIN VUZ ON VUZ."Код" = Tp_fv."Код"
                INNER JOIN Tp_nir ON Tp_nir."Код" = Tp_fv."Код"  -- Добавлено
                WHERE {} = ?
            '''.format(column_name)
        else:
            query = '''
                SELECT *
                FROM ({}) AS prev
                INNER JOIN Tp_fv ON prev."Код" = Tp_fv."Код"
                INNER JOIN VUZ ON VUZ."Код" = Tp_nir."Код"
                WHERE {} = ?
            '''.format(previous_results, column_name)

        c.execute(query, (selected_value,))

        model = QSqlQueryModel()
        model.setQuery(c)
        self.tableView.setModel(model)  # Используйте self.tableView

        previous_results = "SELECT * FROM ({})".format(model.query().lastQuery())  # Сохраните запрос для следующего цикла

    conn.close()


def delete_string_in_table(table_view, table_model):
    """Удаление строки из таблицы."""
    try:
        selection_model = table_view.selectionModel()
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        prompt = QMessageBox.question(None,"Удаление строки",f"Вы уверены, что желаете удалить строку?")
        if prompt == QMessageBox.StandardButton.Yes:
            for row in sorted(index.row() for index in selected_rows)[::-1]:
                table_model.removeRow(row)
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
    return False


def print_vuz_summary():
    """Вывод данных из таблицы VUZ_Summary в консоль."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    query = "SELECT * FROM VUZ_Summary"
    c.execute(query)

    rows = c.fetchall()

    # Вывод заголовков
    print(f"{'Сокращенное имя':<30} {'Сумма планового финансирования':<30} {'Сумма количества НИР':<30} {'Сумма фактического финансирования':<30}")
    print("=" * 120)

    # Вывод данных
    for row in rows:
        # Заменяем None на пустую строку
        row_display = [str(value) if value is not None else '' for value in row]
        print(f"{row_display[0]:<30} {row_display[1]:<30} {row_display[2]:<30} {row_display[3]:<30}")

    conn.close()

def print_grnti_summary():
    """Вывод данных из таблицы GRNTI_Summary в консоль."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    query = "SELECT * FROM GRNTI_Summary"
    c.execute(query)

    rows = c.fetchall()

    # Вывод заголовков
    print(f"{'Код рубрики':<15} {'Название рубрики':<30} {'Количество НИР':<20} {'Сумма планового финансирования':<30}")
    print("=" * 120)

    # Вывод данных
    for row in rows:
        # Заменяем None на пустую строку
        row_display = [str(value) if value is not None else '' for value in row]
        print(f"{row_display[0]:<15} {row_display[1]:<30} {row_display[2]:<20} {row_display[3]:<30}")

    conn.close()


def print_nir_character_summary():
    """Вывод данных из таблицы NIR_Character_Summary в консоль."""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    query = "SELECT * FROM NIR_Character_Summary"
    c.execute(query)

    rows = c.fetchall()

    # Вывод заголовков
    print(f"{'Характер':<30} {'Количество НИР':<20} {'Сумма планового финансирования':<30}")
    print("=" * 80)

    # Вывод данных
    for row in rows:
        # Заменяем None на пустую строку
        row_display = [str(value) if value is not None else '' for value in row]
        print(f"{row_display[0]:<30} {row_display[1]:<20} {row_display[2]:<30}")

    conn.close()

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
    print_nir_character_summary()

prepare_tables()