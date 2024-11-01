import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QInputDialog,
                             QAbstractItemView, QComboBox, QTextEdit, QHeaderView)
from PyQt6 import uic
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt6.QtGui import QKeyEvent, QTextCursor


class CustomTextEdit(QTextEdit):
    def keyPressEvent(self, event: QKeyEvent):
        current_text = self.toPlainText()
        key = event.text()

        if key.isdigit() or key == '.':
            parts = current_text.split('.')
            if key == '.':
                if len(parts) < 3:  # Максимум 2 точки
                    super().keyPressEvent(event)
            else:
                if len(parts) < 3:
                    super().keyPressEvent(event)
                else:
                    if len(parts[-1]) < 2:  # Последняя часть должна быть не более 2 цифр
                        super().keyPressEvent(event)
        else:
            return

        self.auto_format()

    def auto_format(self):
        text = self.toPlainText().replace(" ", "")
        if len(text) > 0:
            text = text.replace('.', '')
            formatted_text = ''
            for i in range(len(text)):
                formatted_text += text[i]
                if (i + 1) % 2 == 0 and (i + 1) < len(text):
                    formatted_text += '.'
            self.setPlainText(formatted_text)

            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_form.ui', self)
        self.db_name = 'databases//database.db'
        self.connect_db()
        self.setup_models()
        self.setup_ui()
        self.show()

        # Подключаем сигнал изменения данных в Tp_nir к слоту обновления Tp_fv
        self.models['Tp_nir'].dataChanged.connect(self.update_tp_fv)

    def connect_db(self):
        """Подключение к базе данных."""
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.db_name)
        if not self.db.open():
            print('Не удалось подключиться к базе данных')
            sys.exit(-1)
        print('Подключение успешно')

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
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView_2.setSortingEnabled(True) #new
        self.tableView_2.horizontalHeader().setStretchLastSection(True) #new
        self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents) #new
        self.tableView_2.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) #new

        self.stackedWidget.setCurrentIndex(0)

        # Подключение действий для отображения таблиц
        self.action_show_VUZ.triggered.connect(lambda: self.table_show('VUZ'))
        self.action_show_Tp_nir.triggered.connect(lambda: self.table_show('Tp_nir'))
        self.action_show_grntirub.triggered.connect(lambda: self.table_show('grntirub'))
        self.action_show_Tp_fv.triggered.connect(lambda: self.table_show('Tp_fv'))
        self.tableView_2.setModel(self.models['Tp_nir']) #new

        # Кнопки для добавления
        self.Tp_nir_redact_add_row_btn.clicked.connect(self.open_add_row_menu)
        self.Tp_nir_add_row_menu_save_btn.clicked.connect(self.save_new_row)
        self.Tp_nir_add_row_menu_close_btn.clicked.connect(lambda: self.cancel(self.Tp_nir_add_row_menu))

        self.Tp_nir_add_row_menu_grntiCode_txt = self.findChild(QTextEdit, 'Tp_nir_add_row_menu_grntiCode_txt')
        self.Tp_nir_add_row_menu_grntiCode_txt.deleteLater()
        self.Tp_nir_add_row_menu_grntiCode_txt = CustomTextEdit()
        self.Tp_nir_add_row_menu_grntiCode_txt.setObjectName('Tp_nir_add_row_menu_grntiCode_txt')
        self.Tp_nir_add_row_menu_grntiCode_txt.setParent(self.Tp_nir_add_row_menu)
        self.Tp_nir_add_row_menu_grntiCode_txt.setGeometry(20, 190, 1101, 31)
        self.Tp_nir_add_row_menu_grntiCode_txt.show()

        # Удалить запись
        self.Tp_nir_redact_del_row_btn.clicked.connect(lambda: self.delete_string_in_table(self.tableView))

        # Кнопки для редактирования
        self.Tp_nir_redact_edit_row_btn.clicked.connect(self.tp_nir_redact_edit_row_btn_clicked)
        self.Tp_nir_edit_row_menu_close_btn.clicked.connect(lambda : self.cancel(self.Tp_nir_edit_row_menu))
        self.Tp_nir_edit_row_menu_save_btn.clicked.connect(self.save_edit_row)


        # Фильтр
        self.Tp_nir_redact_filters_btn.clicked.connect(self.filter) #new
        self.Tp_nir_redact_filters_close_btn.clicked.connect(lambda: self.cancel(self.Tp_nir_add_row_menu)) #new

    def on_reset_filter(self):
        self.models['Tp_nir'].setFilter("")
        self.models['Tp_nir'].select()
        self.tableView.setModel(self.models['Tp_nir'])
        self.tableView.reset()
        self.tableView.show()

    def open_add_row_menu(self):
        """Сброс состояния и открытие меню добавления строки."""
        self.reset_add_row_menu()  # Сброс состояния меню
        self.fill_comboboxes_tp_nir_add_row_menu()  # Заполнение комбобоксов
        self.show_menu(self.Tp_nir_add_row_menu, 1)  # Показ меню

    def reset_add_row_menu(self):
        """Сброс состояния полей ввода в меню добавления."""
        self.Tp_nir_add_row_menu_grntiNumber_txt.clear()
        self.Tp_nir_add_row_menu_grntiNature_cmb.setCurrentIndex(0)
        self.Tp_nir_add_add_row_menu_grntiHead_txt.clear()
        self.Tp_nir_add_row_menu_grntiCode_txt.clear()
        self.Tp_nir_add_row_menu_grntiName_txt.clear()
        self.Tp_nir_add_row_menu_grntiHeadPost_txt.clear()
        self.Tp_nir_add_row_menu_plannedFinancing_txt.clear()
        self.Tp_nir_add_row_menu_VUZcode_name_cmb.setCurrentIndex(0)

    def show_menu(self, menu, index):
        """Отображение указанного меню."""
        self.stackedWidget.setCurrentIndex(index)
        menu.activateWindow()

    def tp_nir_redact_edit_row_btn_clicked(self):
        """Обработчик нажатия кнопки редактирования строки."""
        self.show_menu(self.Tp_nir_edit_row_menu, 2)
        self.fill_comboboxes_tp_nir_edit_row_menu()  # Заполнение комбобоксов перед заполнением виджетов
        self.fill_widgets_from_selected_row()

    def fill_comboboxes_tp_nir_add_row_menu(self):
        """Заполнение комбобоксов в меню добавления строки."""
        self.Tp_nir_add_row_menu_VUZcode_name_cmb.clear()
        self.Tp_nir_add_row_menu_grntiNature_cmb.clear()

        # Заполнение комбобокса VUZ
        query = "SELECT Код, Сокращенное_имя FROM VUZ"
        model = self.models['VUZ']
        model.setFilter("")  # Сброс фильтра
        model.select()

        for row in range(model.rowCount()):
            cod = model.record(row).value("Код")
            name = model.record(row).value("Сокращенное_имя")
            self.Tp_nir_add_row_menu_VUZcode_name_cmb.addItem(f"{cod} - {name}", cod)

        print("Заполнен комбобокс VUZ")  # Отладка

        # Заполнение комбобокса для характера
        self.Tp_nir_add_row_menu_grntiNature_cmb.addItem("П - Природное")
        self.Tp_nir_add_row_menu_grntiNature_cmb.setItemData(0, "П")
        self.Tp_nir_add_row_menu_grntiNature_cmb.addItem("Р - Развивающее")
        self.Tp_nir_add_row_menu_grntiNature_cmb.setItemData(1, "Р")
        self.Tp_nir_add_row_menu_grntiNature_cmb.addItem("Ф - Фундаментальное")
        self.Tp_nir_add_row_menu_grntiNature_cmb.setItemData(2, "Ф")

        print("Заполнен комбобокс характера")  # Отладка

    def fill_comboboxes_tp_nir_edit_row_menu(self):
        """Заполнение комбобоксов в меню редактирования строки."""
        self.Tp_nir_edit_row_menu_grntiNature_cmb.clear()

        # Заполнение комбобокса для характера
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("П - Природное")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.setItemData(0, "П")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("Р - Развивающее")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.setItemData(1, "Р")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("Ф - Фундаментальное")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.setItemData(2, "Ф")

        print("Заполнен комбобокс характера для редактирования")  # Отладка

    def save_new_row(self):
        """Сохранение новой строки в таблице Tp_nir."""
        # Получаем данные из полей ввода
        grnti_number = self.Tp_nir_add_row_menu_grntiNumber_txt.toPlainText()
        grnti_nature = self.Tp_nir_add_row_menu_grntiNature_cmb.currentData()
        grnti_head = self.Tp_nir_add_add_row_menu_grntiHead_txt.toPlainText()
        grnti_code = self.Tp_nir_add_row_menu_grntiCode_txt.toPlainText()
        grnti_name = self.Tp_nir_add_row_menu_grntiName_txt.toPlainText()
        grnti_head_post = self.Tp_nir_add_row_menu_grntiHeadPost_txt.toPlainText()
        planned_financing = self.Tp_nir_add_row_menu_plannedFinancing_txt.toPlainText()
        vuz_code = self.Tp_nir_add_row_menu_VUZcode_name_cmb.currentData()

        # Проверка на пустые поля
        if not all([grnti_number, grnti_nature, grnti_head, grnti_code, grnti_name, grnti_head_post, planned_financing,
                    vuz_code]):
            self.show_error_message("Пожалуйста, заполните все поля.")
            return

        # Проверка на существование записи
        existing_record_query = '''
            SELECT COUNT(*) FROM Tp_nir WHERE "Код" = ? AND "Номер" = ?
        '''
        query = QSqlQuery()  # Создаем объект QSqlQuery
        query.prepare(existing_record_query)  # Подготавливаем запрос
        query.addBindValue(vuz_code)  # Привязываем значения
        query.addBindValue(grnti_number)

        if not query.exec():  # Выполняем запрос
            self.show_error_message("Ошибка при выполнении запроса: " + query.lastError().text())
            return

        if query.next():  # Переходим к результату
            existing_count = query.value(0)  # Получаем значение COUNT(*)

        if existing_count > 0:
            self.show_error_message("Запись с таким Кодом и Номером уже существует.")
            return

        # Создаем новый словарь для записи
        new_record = {
            'Номер': grnti_number,
            'Характер': grnti_nature,
            'Руководитель': grnti_head,
            'Коды_ГРНТИ': grnti_code,
            'НИР': grnti_name,
            'Должность': grnti_head_post,
            'Плановое_финансирование': planned_financing,
            'Код': vuz_code,
            'Сокращенное_имя': self.Tp_nir_add_row_menu_VUZcode_name_cmb.currentText().split(" - ")[1]
        }

        print("Данные для сохранения:", new_record)

        try:
            # Получаем модель и добавляем новую строку
            model = self.models['Tp_nir']
            row_position = model.rowCount()
            model.insertRow(row_position)

            # Заполняем новую строку данными
            for key, value in new_record.items():
                if value:  # Проверяем, что значение не пустое
                    model.setData(model.index(row_position, model.fieldIndex(key)), value)
                    print(f"Установлено: {key} = {value}")  # Отладка

            # Сохраняем изменения в базе данных
            if not model.submitAll():
                raise Exception(f"Ошибка сохранения данных: {model.lastError().text()}")

            # Устанавливаем выделение на новую строку и обновляем интерфейс
            self.tableView.setCurrentIndex(model.index(row_position, 0))
            self.stackedWidget.setCurrentIndex(0)
            QMessageBox.information(self, "Успех", "Данные успешно сохранены.")

        except Exception as e:
            self.show_error_message(f"Ошибка при сохранении данных: {e}")

    def save_edit_row(self):
        """Сохранение отредактированной строки в таблице."""
        # Получаем данные из полей ввода
        vuz_code = self.Tp_nir_edit_row_menu_VUZcode_txt.toPlainText()
        grnti_number = self.Tp_nir_edit_row_menu_grntiNumber_txt.toPlainText()
        grnti_nature = self.Tp_nir_edit_row_menu_grntiNature_cmb.currentData()
        grnti_head = self.Tp_nir_edit_row_menu_grntiHead_txt.toPlainText()
        grnti_code = self.Tp_nir_edit_row_menu_grntiCode_txt.toPlainText()
        grnti_name = self.Tp_nir_edit_row_menu_grntiName_txt.toPlainText()
        grnti_head_post = self.Tp_nir_edit_row_menu_grntiHeadPost_txt.toPlainText()
        planned_financing = self.Tp_nir_edit_row_menu_plannedFinancing_txt.toPlainText()

        # Проверка на пустые поля
        if not all([vuz_code, grnti_number, grnti_nature, grnti_head, grnti_code, grnti_name, grnti_head_post,
                    planned_financing]):
            self.show_error_message("Пожалуйста, заполните все поля.")
            return

        new_record = {
            'Код': vuz_code,
            'Номер': grnti_number,
            'Характер': grnti_nature,
            'Руководитель': grnti_head,
            'Коды_ГРНТИ': grnti_code,
            'НИР': grnti_name,
            'Должность': grnti_head_post,
            'Плановое_финансирование': planned_financing,
        }

        try:
            # Получаем модель и находим индекс редактируемой строки
            model = self.models['Tp_nir']
            selection_model = self.tableView.selectionModel()
            selected_indexes = selection_model.selectedIndexes()

            if not selected_indexes:
                self.show_error_message("Ошибка: не выбрана строка.")
                return

            selected_row = selected_indexes[0].row()  # Получаем индекс выбранной строки

            # Обновляем данные в модели
            for key, value in new_record.items():
                model.setData(model.index(selected_row, model.fieldIndex(key)), value)

            # Сохраняем изменения в базе данных
            if not model.submitAll():
                raise Exception(f"Ошибка сохранения данных: {model.lastError().text()}")

            # Обновляем интерфейс
            self.tableView.setModel(model)
            self.tableView.setCurrentIndex(model.index(selected_row, 0))
            self.stackedWidget.setCurrentIndex(0)
            QMessageBox.information(self, "Успех", "Данные успешно сохранены.")
        except Exception as e:
            self.show_error_message(f"Ошибка при сохранении данных: {e}")

    def update_tp_fv(self):
        """Обновление данных в таблице Tp_fv на основе изменений в Tp_nir."""
        conn = QSqlDatabase.database()  # Используем подключение к базе данных
        if not conn.isOpen():
            print("Ошибка: база данных не открыта.")
            return

        # Выполняем SQL-запрос для обновления всех необходимых полей в Tp_fv
        query = '''
            UPDATE Tp_fv
            SET 
                "Сокращенное_имя" = (
                    SELECT VUZ."Сокращенное_имя"
                    FROM VUZ
                    WHERE VUZ."Код" = Tp_fv."Код"
                ),
                "Плановое_финансирование" = (
                    SELECT SUM("Плановое_финансирование")
                    FROM Tp_nir
                    WHERE Tp_nir."Код" = Tp_fv."Код"
                ),
                "Количество_НИР" = (
                    SELECT COUNT("Номер")
                    FROM Tp_nir
                    WHERE Tp_nir."Код" = Tp_fv."Код"
                )
        '''

        sql_query = QSqlQuery(conn)  # Создаем объект QSqlQuery
        if not sql_query.exec(query):
            print("Ошибка при выполнении запроса:", sql_query.lastError().text())
            return

        # После обновления, можно перезагрузить данные в Tp_fv
        self.models['Tp_fv'].select()

        print("Таблица Tp_fv обновлена на основе изменений в Tp_nir.")

    def fill_widgets_from_selected_row(self):
        """Заполнение виджетов данными из выбранной строки таблицы."""
        selection_model = self.tableView.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            self.show_error_message("Ошибка: не выбрана строка.")
            return

        # Получаем индекс первой выбранной строки
        selected_row = selected_indexes[0].row()

        # Извлекаем данные из модели
        model = self.models['Tp_nir']

        # Заполняем виджеты данными из выбранной строки
        self.Tp_nir_edit_row_menu_VUZcode_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('Код')))))
        self.Tp_nir_edit_row_menu_VUZ_short_name_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('Сокращенное_имя')))))
        self.Tp_nir_edit_row_menu_grntiNumber_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('Номер')))))

        # Установка текущего значения комбобокса
        grnti_nature = str(model.data(model.index(selected_row, model.fieldIndex('Характер'))))
        index = self.Tp_nir_edit_row_menu_grntiNature_cmb.findData(grnti_nature)
        if index != -1:
            self.Tp_nir_edit_row_menu_grntiNature_cmb.setCurrentIndex(index)

        self.Tp_nir_edit_row_menu_grntiHead_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('Руководитель')))))
        self.Tp_nir_edit_row_menu_grntiCode_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('Коды_ГРНТИ')))))
        self.Tp_nir_edit_row_menu_grntiName_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('НИР')))))
        self.Tp_nir_edit_row_menu_grntiHeadPost_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('Должность')))))
        self.Tp_nir_edit_row_menu_plannedFinancing_txt.setPlainText(
            str(model.data(model.index(selected_row, model.fieldIndex('Плановое_финансирование')))))

    def cancel(self, name_widget):
        """Закрытие окна."""
        self.stackedWidget.setCurrentIndex(0)  # Переключаемся на основной экран

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
        # Get the input from the QTextEdit
        str_cod = self.grnticode_txt.toPlainText().strip()  # Get the text and strip whitespace

        # Check if the input is empty or not a digit
        if not str_cod or not str_cod.isdigit():
            self.show_error_message("Неправильное значение. Пожалуйста, введите численные значения.")
            return

        # Prepare the query for filtering
        query = f'"Коды_ГРНТИ" LIKE "{str_cod}%" '

        # Set the filter on the model and refresh the view
        self.models['Tp_nir'].setFilter(query)
        self.models['Tp_nir'].select()
        self.tableView.setModel(self.models['Tp_nir'])
        self.tableView.reset()
        self.tableView.show()

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

    def filter(self):
        self.show_menu(self.Tp_nir_add_row_menu, 3)


        self.grnticode_txt = self.findChild(QTextEdit, 'grnticode_txt')
        self.filter_by_grnticode_btn.clicked.connect(self.filter_by_cod_grnti)
        self.cancel_filtration_btn.clicked.connect(self.on_reset_filter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
