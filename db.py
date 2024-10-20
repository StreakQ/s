import os
import sqlite3
import csv
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QMessageBox

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connect()

    def connect(self):
        """Connect to the SQLite database."""
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(self.db_name)
        if not db.open():
            raise Exception('Не удалось подключиться к базе данных')

    def create_database(self):
        """Create a new database."""
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        conn = sqlite3.connect(self.db_name)
        conn.commit()
        conn.close()

    def create_table(self, table_creation_query):
        """Create a table in the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(table_creation_query)
        conn.commit()
        conn.close()

    def import_from_csv(self, table_name, csv_file):
        """Import data from a CSV file into a specified table."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        with open(csv_file, mode='r', encoding='cp1251') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            headers = next(reader)  # Skip the header row

            # Create a query string with dynamic number of parameters
            placeholders = ', '.join(['?'] * len(headers))  # Example: "?, ?, ?, ..."
            query = f'INSERT INTO {table_name} VALUES ({placeholders})'

            for row in reader:
                try:
                    cursor.execute(query, row)  # Pass row as parameters
                except sqlite3.IntegrityError as e:
                    print(f"Ошибка на строке {row}: {e}")

        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        """Execute a given SQL query."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_all(self, query):
        """Fetch all results from a given SQL query."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results