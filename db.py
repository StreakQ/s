import os
import sqlite3
import csv
from PyQt6.QtSql import *

db_name = 'databases//database.db'

def create_database():
    if os.path.exists(db_name):
        os.remove(db_name)
    conn = sqlite3.connect(db_name)
    conn.commit()
    conn.close()

def connect_db(db_name_name):
    db_name = QSqlDatabase.addDatabase('QSQLITE')
    db_name.setDatabaseName(db_name_name)
    if not db_name.open():
        print('не удалось подключиться к базе')
        return False
    return db_name

# if not connect_db(db_name):
#     sys.exit(-1)
# else:
#     print('Connection OK')


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
    '''Получение значений выбранного столбца для отображения в выподающем меню GUI'''
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f'''SELECT {column_name}
                FROM Tp_nir INNER JOIN VUZ ON  VUZ."Код" = Tp_nir."Код"
                    ''')
    column = c.fetchall()
    conn.commit()
    conn.close()
    return column

def get_column_name_with_linked_value(value):
    '''Получение имени столбца выбранного значения из GUI'''
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f'''PRAGMA table_info(Tp_nir)''')
    rows1 = c.fetchall()
    c.execute(f'''PRAGMA table_info(VUZ)''')
    rows2 = c.fetchall()
    rows = rows1 + rows2
    for row in rows:
        c.execute(f'''SELECT {row[1]}
                            FROM FROM Tp_fv
                                INNER JOIN VUZ ON VUZ."Код" = Tp_nir."Код"  
                                WHERE {row[1]} = ?''', (value,))
        if c.fetchone():
            return row[1]
    return None

def hard_filter(selected_value):
    '''Фильтрация по области, оркругу, городу, вузу'''
    #selected_value - это значение, выбранное из выпадающего  меню в GUI и переданное в функцию
    # получение из GUI selected_value

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    column_name = get_column_name_with_linked_value(selected_value)
    c.execute(f'''CREATE VIEW table_1 AS
                        SELECT * 
                        FROM Tp_fv
                        INNER JOIN VUZ ON VUZ."Код" = Tp_nir."Код" 
                        WHERE {column_name} = ?''', selected_value)
    rows = c.fetchall()

    # отображение полученных значений в GUI(создание нового экземпляра QSqlTableModel?)
    # получение нового selected_value и  column_name из GUI
    column_name = get_column_name_with_linked_value(selected_value)
    c.execute(f'''CREATE VIEW table_2 AS
                            SELECT * 
                            FROM table_1
                            INNER JOIN VUZ ON VUZ."Код" = table_1."Код" 
                            WHERE {column_name} = ?''', selected_value)
    rows = c.fetchall()

    # отображение полученных значений в GUI(создание нового экземпляра QSqlTableModel?)
    # получение нового selected_value и  column_name из GUI
    column_name = get_column_name_with_linked_value(selected_value)
    c.execute(f'''CREATE VIEW table_3 AS
                               SELECT * 
                               FROM table_2
                               INNER JOIN VUZ ON VUZ."Код" = table_2."Код" 
                               WHERE {column_name} = ?''', selected_value)
    rows = c.fetchall()

    # отображение полученных значений в GUI(создание нового экземпляра QSqlTableModel?)
    # получение нового selected_value и  column_name из GUI
    column_name = get_column_name_with_linked_value(selected_value)
    c.execute(f'''
                               SELECT * 
                               FROM table_3
                               INNER JOIN VUZ ON VUZ."Код" = table_3."Код" 
                               WHERE {column_name} = ?''', selected_value)
    rows = c.fetchall()
    # отображение полученных значений в GUI(создание нового экземпляра QSqlTableModel?)
    conn.commit()
    conn.close()

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





