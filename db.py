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

def create_order_table():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS Order_table')
    c.execute('''
    CREATE TABLE IF NOT EXISTS Order_table (
    "Сокращенное_имя" TEXT DEFAULT NULL,
    "Сумма_фактического_финансирования" INTEGER DEFAULT NULL
    )
    ''')

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
                #print(f"Error on row {row_num}: {e}")
                count += 1
            row_num += 1

    #print(f"Total errors: {count}")
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
                #print(f"Error on row {row_num}: {e}")
                count += 1
            row_num += 1

    #print(f"Total errors: {count}")
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

    #print(f"Total errors: {count}")
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
                #print(f"Error on row {row_num}: {e}")
                count += 1
            row_num += 1

    #print(f"Total errors: {count}")
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
    c.execute('''INSERT INTO Tp_fv ("Код", "Сокращенное_имя", "Плановое_финансирование", "Фактическое_финансирование", "Количество_НИР")
                SELECT 
                    VUZ."Код",
                    VUZ."Сокращенное_имя",
                    SUM(Tp_nir."Плановое_финансирование"),
                    0, 
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

def fill_vuz_summary_db(db):
    """Заполнение таблицы VUZ_Summary только для вузов, которые есть в Tp_nir."""
    query = QSqlQuery(db)  # Используем переданное соединение
    query.exec('DELETE FROM VUZ_Summary')

    # Ваши операции с базой данных
    insert_query = '''
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
    query.exec(insert_query)

    # Добавляем итоговую строку
    query.exec('''
        INSERT INTO VUZ_Summary ("Сокращенное_имя", "Сумма_планового_финансирования", "Сумма_количества_НИР", "Сумма_фактического_финансирования")
        SELECT 
            'ИТОГО',
            SUM("Сумма_планового_финансирования"),
            SUM("Сумма_количества_НИР"),
            SUM("Сумма_фактического_финансирования")
        FROM VUZ_Summary
    ''')
    return True  # Возвращаем True, если все прошло успешно

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

def fill_grnti_summary_db(db):
    """Заполнение таблицы GRNTI_Summary."""
    query = QSqlQuery(db)  # Используем переданное соединение
    query.exec('DELETE FROM GRNTI_Summary')


    insert_query = '''
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
    query.exec(insert_query)
    return True

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

def fill_nir_character_summary_db(db):
    """Заполнение таблицы NIR_Character_Summary."""
    query = QSqlQuery(db)  # Используем переданное соединение
    query.exec('DELETE FROM NIR_Character_Summary')


    insert_query = '''
        INSERT INTO NIR_Character_Summary ("Характер", "Количество_НИР", "Сумма_планового_финансирования")
        SELECT 
            "Характер",
            COUNT("Номер") AS "Количество_НИР",
            SUM("Плановое_финансирование") AS "Сумма_планового_финансирования"
        FROM Tp_nir
        GROUP BY "Характер"
    '''
    query.exec(insert_query)

    # Добавляем итоговую строку
    query.exec('''
        INSERT INTO NIR_Character_Summary ("Характер", "Количество_НИР", "Сумма_планового_финансирования")
        SELECT 
            'ИТОГО',
            SUM("Количество_НИР"),
            SUM("Сумма_планового_финансирования")
        FROM NIR_Character_Summary
    ''')

    return True




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

def grnti_to_cmb():
    # Создаем или открываем базу данных
    connection = sqlite3.connect('databases//database.db')

    # Создаем курсор
    cursor = connection.cursor()

    # Извлекаем данные из столбцов 'Код_рубрики' и 'Рубрика' за один запрос
    cursor.execute("SELECT Код_рубрики, Рубрика FROM grntirub")
    records = cursor.fetchall()  # Получаем все записи в виде списка кортежей

    # Формируем список строк в формате "код - название" и возвращаем кортежи
    grnti_to_cmb = [(f'{code:02}', f'{code:02} - {name}') for code, name in records]

    connection.commit()
    connection.close()

    #print("grnti_to_cmb:", grnti_to_cmb)  # Отладочное сообщение
    return grnti_to_cmb





def log_lock_status(cursor):
    """Функция для логирования состояния блокировок."""
    cursor.execute('PRAGMA lock_status;')
    lock_status = cursor.fetchall()
    print("Состояние блокировок:")
    for status in lock_status:
        print(status)


def log_database_list(cursor):
    """Функция для логирования списка баз данных."""
    cursor.execute('PRAGMA database_list;')
    databases = cursor.fetchall()
    print("Список баз данных:")
    for db in databases:
        print(db)


def fill_vuz_summary_with_filters(grnti_conditions, complex_conditions):
    """Заполнение таблицы VUZ_Summary с учетом условий фильтрации."""

    with sqlite3.connect(db_name, timeout=10) as conn:
        c = conn.cursor()
        c.execute('PRAGMA busy_timeout = 3000')

        log_lock_status(c)
        log_database_list(c)

        try:
            # Начинаем транзакцию
            c.execute('BEGIN IMMEDIATE;')
            c.execute('DELETE FROM VUZ_Summary')

            # Формируем условия фильтрации
            filter_conditions = []
            if grnti_conditions:
                filter_conditions.extend([f'Tp_nir."Коды_ГРНТИ" LIKE "{cod}%"' for cod in grnti_conditions])
            if complex_conditions:
                filter_conditions.extend(complex_conditions)

            # Создаем строку условий для SQL-запроса
            where_clause = ''
            if filter_conditions:
                where_clause = 'WHERE ' + ' AND '.join(filter_conditions)
            print(where_clause)

            query = f'''
                INSERT INTO VUZ_Summary ("Сокращенное_имя", "Сумма_планового_финансирования", "Сумма_количества_НИР", "Сумма_фактического_финансирования")
                SELECT 
                    VUZ."Сокращенное_имя",
                    SUM(Tp_nir."Плановое_финансирование") AS "Сумма_планового_финансирования",
                    COUNT(Tp_nir."Номер") AS "Сумма_количества_НИР",
                    SUM(Tp_fv."Фактическое_финансирование") AS "Сумма_фактического_финансирования"
                FROM VUZ
                LEFT JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
                LEFT JOIN Tp_fv ON VUZ."Код" = Tp_fv."Код"
                {where_clause} 
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
        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")
            conn.rollback()  # Откат транзакции в случае ошибки
        finally:
            # Логируем состояние блокировок после завершения операций
            log_lock_status(c)
            log_database_list(c)
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


prepare_tables()