import os
import sqlite3
import csv
from PyQt6.QtSql import *
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QTextEdit
from PyQt6.QtCore import Qt

db_name = 'databases//database.db'

def create_database():
    if os.path.exists(db_name):
        os.remove(db_name)
    conn = sqlite3.connect(db_name)
    conn.commit()
    conn.close()

def connect_db(db_name_name):
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name_name)
    if not db.open():
        print('не удалось подключиться к базе')
        return False
    return db

def create_table_tp_nir():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS Tp_nir')
    c.execute('''
    CREATE TABLE IF NOT EXISTS Tp_nir (
    "Код" INTEGER,
    "Номер" INTEGER,
    "Характер" TEXT ,
    "Сокращенное_имя" TEXT DEFAULT NULL,
    "Руководитель" TEXT ,
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
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS VUZ')
    c.execute('''
       CREATE TABLE IF NOT EXISTS VUZ (
       "Код" INTEGER,
       "Наименование" , 
        "Полное_имя", 
        "Сокращенное_имя",
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

def import_table_tp_nir_from_csv():
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

def connect_db(db_name):
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print('не удалось подключиться к базе')
        return False
    return db

def get_column_values_from_table(column_name):
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
    '''Получение имени столбца выбранного значения из GUI'''
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("PRAGMA table_info(Tp_nir)")
        rows1 = c.fetchall()
        c.execute("PRAGMA table_info(VUZ)")
        rows2 = c.fetchall()
        rows = rows1 + rows2
        for row in rows:
            query = "SELECT ? FROM Tp_nir INNER JOIN VUZ ON VUZ.Код = Tp_nir.Код WHERE ? = ?"
            c.execute(query, (row[1], row[1], value))
            if c.fetchone():
                return row[1]
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()
    return None

def hard_filter(selected_values):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    previous_results = None
    for selected_value in selected_values:
        column_name = get_column_name_with_linked_value(selected_value)

        if previous_results is None:
            query = '''
                SELECT *
                FROM Tp_fv
                INNER JOIN VUZ ON VUZ."Код" = Tp_nir."Код"
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
        tableView.setModel(model)

        previous_results = c.fetchall()

    conn.close()

def delete_string_in_table(table_view, table_model):
    '''Удаление всей строки таблицы'''
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

def prepare_tables():
    create_database()

    create_table_tp_nir()
    create_table_vuz()
    create_table_grntirub()
    create_table_tp_fv()

    import_table_tp_nir_from_csv()
    import_table_vuz_from_csv()
    import_table_grntirub_from_csv()
    import_table_tp_fv_from_csv()

    make_correct_cod_grnti()
    input_short_name_from_vuz()
    fill_tp_fv()

def codes():
    conn = sqlite3.connect('databases//database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Код FROM VUZ")
    codes = cursor.fetchall()
    code_list=[code[0] for code in codes]
    #print(code_list)
    conn.close()
    return code_list

def column():
    conn = sqlite3.connect('databases//database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Сокращенное_имя FROM VUZ")
    names = cursor.fetchall()
    name_list=[name[0] for name in names]
    #print(name_list)
    conn.close()
    return name_list

def Federal_District():
    conn = sqlite3.connect('databases//database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Регион FROM VUZ")
    names = cursor.fetchall()
    region_list = [name[0] for name in names]
    # print(name_list)
    conn.close()
    return region_list

def Federation_subject():
    conn = sqlite3.connect('databases//database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Область FROM VUZ")
    names = cursor.fetchall()
    subject_list = [name[0] for name in names]
    # print(name_list)
    conn.close()
    return subject_list


def City_list():
    conn = sqlite3.connect('databases//database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Город FROM VUZ")
    names = cursor.fetchall()
    city_list = [name[0] for name in names]
    # print(name_list)
    conn.close()
    return city_list


def VUZ_list():
    conn = sqlite3.connect('databases//database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Сокращенное_имя FROM VUZ")
    names = cursor.fetchall()
    VUZ_list=[name[0] for name in names]
    #print(name_list)
    conn.close()
    return VUZ_list