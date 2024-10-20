import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QInputDialog,
                             QAbstractItemView, QMenu, QComboBox, QTextEdit, QHeaderView, QWidget)
from PyQt6 import uic
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt
import re


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_form.ui', self)
        self.db_name = 'databases//database.db'
        self.connect_db()
        self.setup_models()
        self.setup_ui()
        self.show()

    def connect_db(self):
        """Подключение к базе данных."""
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.db_name)
        if not self.db.open():
            print('Не удалось подключиться к базе')
            sys.exit(-1)
        print('Connection OK')

    def setup_models(self):
        """Настройка моделей для таблиц."""
        self.models = {
            'VUZ': QSqlTableModel(self),
            'Tp_nir': QSqlTableModel(self),
            'grntirub': QSqlTableModel(self),
            'Tp_fv': QSqlTableModel(self)
        }
        for name, model in self.models.items():
            model.setTable(name)
            model.select()

    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Настройка таблицы
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Установка начального индекса для QStackedWidget
        self.stackedWidget.setCurrentIndex(0)  # Установите нужный индекс, например, 0 для первой страницы

        # Подключение действий для отображения таблиц
        self.action_show_VUZ.triggered.connect(lambda: self.table_show('VUZ'))
        self.action_show_Tp_nir.triggered.connect(lambda: self.table_show('Tp_nir'))
        self.action_show_grntirub.triggered.connect(lambda: self.table_show('grntirub'))
        self.action_show_Tp_fv.triggered.connect(lambda: self.table_show('Tp_fv'))

    # Подключение кнопок
        # меню добавить
        self.Tp_nir_redact_add_row_btn.clicked.connect(lambda: self.show_menu(self.Tp_nir_add_row_menu))
        self.Tp_nir_add_row_menu_save_btn.clicked.connect(self.save_new_row)
        self.Tp_nir_add_row_menu_close_btn.clicked.connect(self.cancel_save_new_row)

        #удалить запись
        self.Tp_nir_redact_del_row_btn.clicked.connect(lambda: self.delete_string_in_table(self.tableView))

        # Заполнение комбобоксов
        #self.populate_comboboxes()

    def show_menu(self, menu):
        """Отображение указанного меню."""
        self.stackedWidget.setCurrentIndex(1)
        menu.activateWindow()


    def save_new_row(self):
        """Сохранение новой строки в таблице Tp_nir."""
        # Получаем данные из полей ввода
        grnti_number = self.Tp_nir_add_row_menu_grntiNumber_txt.toPlainText()
        grnti_nature = self.Tp_nir_add_row_menu_grntiNature_cmb.currentText()
        grnti_head = self.Tp_nir_add_add_row_menu_grntiHead_txt.toPlainText()
        grnti_code = self.Tp_nir_add_row_menu_grntiCode_txt.toPlainText()
        grnti_name = self.Tp_nir_add_row_menu_grntiName_txt.toPlainText()
        grnti_head_post = self.Tp_nir_add_row_menu_grntiHeadPost_txt.toPlainText()
        planned_financing = self.Tp_nir_add_row_menu_plannedFinancing_txt.toPlainText()

        # Создаем новую запись
        new_record = {
            'grntiNumber': grnti_number,
            'grntiNature': grnti_nature,
            'grntiHead': grnti_head,
            'grntiCode': grnti_code,
            'grntiName': grnti_name,
            'grntiHeadPost ': grnti_head_post,
            'plannedFinancing': planned_financing
        }

        # Добавляем новую строку в модель
        model = self.models['Tp_nir']
        model.insertRow(model.rowCount())  # Добавляем новую строку в конец
        for key, value in new_record.items():
            model.setData(model.index(model.rowCount() - 1, model.fieldIndex(key)), value)

        # Сохраняем изменения в базе данных
        model.submitAll()
        new_index = model.index(model.rowCount() - 1, 0)
        self.tableView.setCurrentIndex(new_index)
        self.Tp_nir_add_row_menu.close()
        self.stackedWidget.setCurrentIndex(0)

    def cancel_save_new_row(self):
        """Отмена сохранения данных и закрытие окна ."""
        # Очистка полей ввода
        input_fields = {
            'grntiNumber': self.Tp_nir_add_row_menu_grntiNumber_txt,
            'grntiNature': self.Tp_nir_add_row_menu_grntiNature_cmb,
            'grntiHead': self.Tp_nir_add_add_row_menu_grntiHead_txt,
            'grntiCode': self.Tp_nir_add_row_menu_grntiCode_txt,
            'grntiName': self.Tp_nir_add_row_menu_grntiName_txt,
            'grntiHeadPost': self.Tp_nir_add_row_menu_grntiHeadPost_txt,
            'plannedFinancing': self.Tp_nir_add_row_menu_plannedFinancing_txt
        }

        # Очистка полей
        self.clear_input_fields(input_fields)

        # Закрытие меню
        self.Tp_nir_add_row_menu.close()
        self.stackedWidget.setCurrentIndex(0)

    def clear_input_fields(self, input_fields):
        """Очистка указанных полей ввода."""
        for field in input_fields.values():
            if isinstance(field, QTextEdit):
                field.clear()  # Очищаем QTextEdit
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(0)  # Сбрасываем QComboBox


    def table_show(self, table_name):
        """Отображение таблицы."""
        self.tableView.setModel(self.models[table_name])


    def filter_by_cod_grnti(self):
        """Фильтрация по коду ГРНТИ."""
        while True:
            str_cod, ok = QInputDialog.getText(None, "Введите значение",
                                               'Введите весь код ГРНТИ или его часть без разделителей и пробелов')
            if not ok:
                return
            if str_cod is None or not str_cod.isdigit():
                self.show_error_message("Неправильное значение. Пожалуйста, введите численные значения.")
                return
            str_cod = str_cod.strip()
            str_cod = self.add_delimiters_to_grnti_code(str_cod)
            query = f' "Коды_ГРНТИ" LIKE "{str_cod}%" OR "Коды_ГРНТИ" LIKE ";{str_cod}%" '
            self.models['Tp_nir'].setFilter(query)
            self.models['Tp_nir'].select()
            self.tableView.setModel(self.models['Tp_nir'])
            self.tableView.reset()
            self.tableView.show()
            break

    def show_error_message(self, message):
        """Отображение ошибочного сообщения."""
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec()

    def delete_string_in_table(self, table_view):
        """Удаление строки из таблицы с подтверждением."""
        selection_model = table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            self.show_error_message("Ошибка: не выбран текущий элемент")
            return

        confirmation_box = QMessageBox(self)
        confirmation_box.setWindowTitle("Подтверждение удаления")
        confirmation_box.setText("Вы уверены, что хотите удалить выбранную строку?")

        delete_button = confirmation_box.addButton("Удалить", QMessageBox.ButtonRole.AcceptRole)
        confirmation_box.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)
        confirmation_box.exec()

        if confirmation_box.clickedButton() == delete_button:
            table_view.model().removeRow(selected_indexes[0].row())

    def save_data(self):
        """Сохранение данных."""
        for model in self.models.values():
            model.submitAll()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
