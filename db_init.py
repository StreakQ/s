from db import DatabaseManager

def main():
    db_manager = DatabaseManager('databases//database.db')
    db_manager.create_database()

# Создание таблиц
db_manager.create_table('''
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

db_manager.create_table('''
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

db_manager.create_table('''
    CREATE TABLE IF NOT EXISTS grntirub (
        "Код_рубрики" INTEGER PRIMARY KEY,
        "Рубрика" TEXT
    )
''')

db_manager.create_table('''
    CREATE TABLE IF NOT EXISTS Tp_fv (
        "Код" INTEGER PRIMARY KEY,
        "Сокращенное_имя" TEXT,
        "Плановое_финансирование" INTEGER,
        "Фактическое_финансирование" INTEGER,
        "Количество_НИР" INTEGER
    )
''')

# Импорт данных из CSV
db_manager.import_from_csv('Tp_nir', 'databases//Tp_nir.csv')
db_manager.import_from_csv('VUZ', 'databases//VUZ.csv')
db_manager.import_from_csv('grntirub', 'databases//grntirub.csv')
db_manager.import_from_csv('Tp_fv', 'databases//Tp_fv.csv')

if __name__ == '__main__':
    main()