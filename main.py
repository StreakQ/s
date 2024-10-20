import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QInputDialog,
                             QAbstractItemView, QMenu, QComboBox, QTextEdit, QHeaderView, QWidget)
from PyQt6 import uic
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_form.ui', self)
        self.db_name = 'databases//database.db'
        self.connect_db()
        self.setup_models()
        self.setup_ui()
        self.show()
        self.Tp_nir_add_row_menu = QWidget(self)  # Убедитесь, что родитель установлен

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
        self.Tp_nir_redact_add_row_btn.clicked.connect(lambda: self.show_menu(self.Tp_nir_add_row_menu))
        self.Tp_nir_add_row_menu_save_btn.clicked.connect(self.save_new_row)
        self.Tp_nir_add_row_menu_close_btn.clicked.connect(self.cancel_save_new_row)
        self.Tp_nir_redact_del_row_btn.clicked.connect(lambda: self.delete_string_in_table(self.tableView))

        # Заполнение комбобоксов, если необходимо
        # self.populate_comboboxes()

    def show_menu(self, menu):
        """Отображение указанного меню."""
        print("Пытаемся показать меню...")
        menu.setVisible(True)
        menu.setStyleSheet("")  # Удалите все стили
        menu.show()
        menu.raise_()
        menu.activateWindow()
        print("Меню показано.")

    def save_new_row(self):
        """Сохранение новой строки в таблице."""
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

        new_index = model.index(model.rowCount() - 1, 0)  # Исправлено на правильный индекс
        self.tableView.setCurrentIndex(new_index)
        self.Tp_nir_add_row_menu.close()

    def cancel_save_new_row(self):
        """Отмена сохранения данных и закрытие окна."""
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
        self.Tp_nir_add_row_menu.setVisible(False)

    def clear_input_fields(self, input_fields):
        """Очистка указанных полей ввода."""
        for field in input_fields.values():
            if isinstance(field, QTextEdit):
                field.clear()  # Очищаем QTextEdit
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(0)  # Сбрасываем QComboBox

    def populate_comboboxes(self):
        """Заполнение комбобоксов сложного фильтра."""
        self.Tp_nir_add_grntiNature_comboBox.addItems(
            ['прикладное исследование (П)', 'экспериментальная разработка (Р)', 'фундаментальное исследование (Ф)'])
        self.Tp_nir_add_VUZcode_name_comboBox.addItems([str(i) + ' ' + var for var, i in zip(name_list, code_list)])
        self.Federal_District_comboBox.addItems(region_list)
        self.Federation_subject_comboBox.addItems(subject_list)
        self.City_comboBox.addItems(City_list)
        self.VUZ_comboBox.addItems(VUZ_list)

        # Установка редактируемости комбобоксов
        for combo in [self.Tp_nir_add_VUZcode_name_comboBox, self.Federal_District_comboBox,
                      self.Federation_subject_comboBox, self.City_comboBox, self.VUZ_comboBox]:
            combo.setEditable(True)

    def table_show(self, table_name):
        """Отображение таблицы."""
        self.tableView.setModel(self.models[table_name])

    def input_cod_grnti(self, table):
        """Ввод кода ГРНТИ."""
        selection_model = table.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            self.show_error_message("Ошибка: не выбран текущий элемент")
            return

        current_index = selected_indexes[0]
        record = table.model().record(current_index.row())
        current_value = record.value(current_index.column())

        menu = QMenu()
        clear_action = menu.addAction("Очистить ячейку")
        add_new_code_action = menu.addAction("Добавить новый код ГРНТИ")
        action = menu.exec(table.mapToGlobal(table.visualRect(current_index).center()))

        if action == clear_action:
            table.model().setData(current_index, "", Qt.ItemDataRole.EditRole)
        elif action == add_new_code_action:
            while True:
                cod, ok = QInputDialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ из шести цифр '
                                                                         'без разделителей и пробелов')
                if not ok:
                    break
                if cod is None or not cod.isdigit() or len(cod) != 6:
                    self.show_error_message("Неверный ввод: пожалуйста, введите 6-значный код")
                    continue
                cod = self.add_delimiters_to_grnti_code(cod)
                result = str(current_value) + str(cod)
                table .model().setData(current_index, result.strip(), Qt.ItemDataRole.EditRole)
                break

    def add_delimiters_to_grnti_code(self, string):
        """Добавление разделителей в код ГРНТИ."""
        if len(string) == 2:
            return "{}.".format(string)
        elif len(string) == 4:
            return "{}.{}".format(string[:2], string[2:])
        else:
            return "{}.{}.{}".format(string[:2], string[2:4], string[4:])

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

        # Создание диалогового окна
        confirmation_box = QMessageBox(self)
        confirmation_box.setWindowTitle("Подтверждение удаления")
        confirmation_box.setText("Вы уверены, что хотите удалить выбранную строку?")


        # Добавляем пользовательскую кнопку "Удалить"
        delete_button = confirmation_box.addButton("Удалить", QMessageBox.ButtonRole.AcceptRole)
        confirmation_box.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)

        # Отображение диалогового окна и получение результата
        confirmation_box.exec()

        # Проверяем, какая кнопка была нажата
        if confirmation_box.clickedButton() == delete_button:
            # Удаление строки, если пользователь подтвердил
            table_view.model().removeRow(selected_indexes[0].row())

    def save_data(self):
        """Сохранение данных."""
        for model in self.models.values():
            model.submitAll()

    def edit_row(self, tableView, edit_button, Tp_nir_redact_VUZcode_textEdit, Tp_nir_redact_VUZshortName_textEdit,
                 Tp_nir_add_grntiNumber_textEdit_2, Tp_nir_add_grntiNature_comboBox_2,
                 Tp_nir_add_grntiHead_textEdit_2, Tp_nir_add_grntiCode_textEdit_2,
                 Tp_nir_add_grntiName_textEdit_2, Tp_nir_add_grntiHead_textEdit,
                 Tp_nir_add_grntiHeadPost_textEdit_2, Tp_nir_add_plannedFinancing_textEdit_2):
        """Редактирование строки."""
        selection_model = tableView.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            self.show_error_message("Ошибка: не выбран текущий элемент")
            return
        current_index = selected_indexes[0]
        record = tableView.model().record(current_index.row())
        record.setValue('VUZcode', Tp_nir_redact_VUZcode_textEdit.text())
        record.setValue('VUZshortName', Tp_nir_redact_VUZshortName_textEdit.text())
        record.setValue('grntiNumber', Tp_nir_add_grntiNumber_textEdit_2.text())
        record.setValue('grntiNature', Tp_nir_add_grntiNature_comboBox_2.currentText())
        record.setValue('grntiHead', Tp_nir_add_grntiHead_textEdit_2.text())
        record.setValue('grntiCode', Tp_nir_add_grntiCode_textEdit_2.text())
        record.setValue('grntiName', Tp_nir_add_grntiName_textEdit_2.text())
        record.setValue('grntiHead ', Tp_nir_add_grntiHead_textEdit.text())
        record.setValue('grntiHeadPost', Tp_nir_add_grntiHeadPost_textEdit_2.text())
        record.setValue('plannedFinancing', Tp_nir_add_plannedFinancing_textEdit_2.text())
        tableView.model().setRecord(current_index.row(), record)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
