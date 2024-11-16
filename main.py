import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QInputDialog,
                             QAbstractItemView, QComboBox, QTextEdit, QHeaderView, QPushButton, QVBoxLayout,
                             QHBoxLayout)
from PyQt6 import uic
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery,QSqlQueryModel
from PyQt6.QtGui import QKeyEvent, QTextCursor
import sqlite3
import re
from db import *

class CustomTextEdit(QTextEdit):
    def keyPressEvent(self, event: QKeyEvent):
        current_text = self.toPlainText()
        key = event.text()

        # Обработка клавиш Backspace и Delete
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            super().keyPressEvent(event)
            return

        if key.isdigit() or key == '.' or key == ';':
            parts = current_text.split(';')

            # Обработка ввода точки с запятой
            if key == ';':
                if len(parts) < 2:  # Максимум 2 кода
                    super().keyPressEvent(event)
            else:
                # Обработка ввода цифр и точек
                if len(parts) == 1:  # Первый код
                    first_part = parts[0].split('.')
                    if key == '.':
                        if len(first_part) < 3:  # Максимум 2 точки в первом коде
                            super().keyPressEvent(event)
                    else:  # Ввод цифр
                        super().keyPressEvent(event)

                    # Автоматически добавляем точку с запятой после первого кода
                    if len(parts[0]) >= 8:  # Если длина кода больше или равна 8, добавляем точку с запятой
                        self.setPlainText(current_text + ';')
                        cursor = self.textCursor()
                        cursor.movePosition(QTextCursor.MoveOperation.End)
                        self.setTextCursor(cursor)
                        return

                elif len(parts) == 2:  # Второй код
                    second_part = parts[1].split('.')
                    if key == '.':
                        if len(second_part) < 3:  # Максимум 2 точки во втором коде
                            super().keyPressEvent(event)
                    else:  # Ввод цифр
                        # Запрещаем ввод больше 8 символов во втором коде
                        if len(parts[1]) < 9:
                            super().keyPressEvent(event)
            self.auto_format()

        else:
            return

    def auto_format(self):
        text = self.toPlainText().replace(" ", "")
        if len(text) > 0:
            parts = text.split(';')
            formatted_parts = []

            for part in parts:
                part = part.replace('.', '')  # Убираем точки для форматирования
                formatted_part = ''
                for i in range(len(part)):
                    formatted_part += part[i]
                    if (i + 1) % 2 == 0 and (i + 1) < len(part):
                        formatted_part += '.'
                if len(formatted_part) > 8:
                    formatted_part = formatted_part[:8]
                formatted_parts.append(formatted_part)

            self.setPlainText('; '.join(formatted_parts))  # Объединяем части с точкой с запятой

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

        # Инициализация атрибутов для отслеживания изменений в комбобоксах
        self.vuz_selected = False
        self.region_selected = False
        self.city_selected = False
        self.obl_selected = False

        # Инициализация флагов для отслеживания изменений
        self.vuz_changed = False
        self.region_changed = False
        self.city_changed = False
        self.obl_changed = False

        self.models['Tp_nir'].dataChanged.connect(self.update_tp_fv)
        self.models['Tp_nir'].dataChanged.connect(self.update_summary_tables)

        self.saved_filter_conditions = []  # Список для хранения условий фильтрации






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
            'Tp_fv': QSqlTableModel(self),
            'VUZ_Summary': QSqlTableModel(self),
            'GRNTI_Summary': QSqlTableModel(self),
            'NIR_Character_Summary': QSqlTableModel(self)

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
        self.tableView_2.setSortingEnabled(True)  # New
        self.tableView_2.horizontalHeader().setStretchLastSection(True)  # New
        self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # New
        self.tableView_2.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # New

        self.stackedWidget.setCurrentIndex(0)


        # Подключение действий для отображения таблиц
        self.action_show_VUZ.triggered.connect(lambda: self.table_show('VUZ'))
        self.action_show_Tp_nir.triggered.connect(lambda: self.table_show('Tp_nir'))
        self.action_show_grntirub.triggered.connect(lambda: self.table_show('grntirub'))
        self.action_show_Tp_fv.triggered.connect(lambda: self.table_show('Tp_fv'))
        self.tableView_2.setModel(self.models['Tp_nir'])  # New


        self.po_rubrikam.triggered.connect(lambda: self.table_show('GRNTI_Summary'))
        self.po_character.triggered.connect(lambda: self.table_show('NIR_Character_Summary'))

        # Кнопки для добавления
        self.Tp_nir_redact_add_row_btn.clicked.connect(self.open_add_row_menu)
        self.Tp_nir_add_row_menu_save_btn.clicked.connect(self.save_new_row)
        self.Tp_nir_add_row_menu_close_btn .clicked.connect(lambda: self.cancel(self.Tp_nir_add_row_menu))


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
        self.Tp_nir_edit_row_menu_close_btn.clicked.connect(lambda: self.cancel(self.Tp_nir_edit_row_menu))
        self.Tp_nir_edit_row_menu_save_btn.clicked.connect(self.save_edit_row)

        # Фильтр
        self.Tp_nir_redact_filters_btn.clicked.connect(self.filter)  # New

        #Анализ
        self.save_filter_btn.clicked.connect(self.save_filter_conditions)  # Подключаем кнопку сохранения фильтров
       # self.apply_filter_btn.clicked.connect(self.apply_saved_filters)
        self.po_VUZ.triggered.connect(lambda: self.table_show('VUZ_Summary'))

    def table_show(self, table_name):
        """Отображение таблицы и управление видимостью кнопки."""
        if table_name == 'VUZ_Summary':
            self.tableView.setModel(self.models['VUZ_Summary'])
            self.apply_filter_btn.show()  # Показываем кнопку при открытии VUZ_Summary
            self.apply_filter_btn.raise_()  # Поднимаем кнопку на передний план
            self.models['VUZ_Summary'].select()
        else:
            self.show_other_table(table_name)

    def show_other_table(self, table_name):
        """Метод для отображения других таблиц (например, VUZ, Tp_nir и т.д.)."""
        self.apply_filter_btn.hide()  # Скрываем кнопку, если открывается другая таблица
        self.tableView.setModel(self.models[table_name])
        self.models[table_name].select()  # Обновляем модель


    def save_filter_conditions(self):
        """Сохранение условий фильтрации по коду ГРНТИ."""
        str_cod = self.grnticode_txt.toPlainText().strip()
        if str_cod:
            self.saved_filter_conditions.append(str_cod)
            print(f"Сохранено условие фильтрации: {str_cod}")
        else:
            self.show_error_message("Введите код ГРНТИ для сохранения условия фильтрации.")

    def apply_saved_filters(self):
        """Применение сохраненных условий фильтрации к таблице VUZ_Summary."""
        if not self.saved_filter_conditions:
            self.show_error_message("Нет сохраненных условий фильтрации.")
            return

        # Формируем фильтр на основе сохраненных условий
        filter_conditions = [f'"Коды_ГРНТИ" LIKE "{cod}%"' for cod in self.saved_filter_conditions]
        query = ' AND '.join(filter_conditions)

        # Применяем фильтр к модели VUZ_Summary
        self.models['VUZ_Summary'].setFilter(query)
        self.models['VUZ_Summary'].select()  # Обновляем модель
        self.tableView.setModel(self.models['VUZ_Summary'])  # Устанавливаем модель в таблицу
        print("Применены сохраненные условия фильтрации к VUZ_Summary.")

    def update_summary_tables(self):
        """Обновление таблиц VUZ_Summary, GRNTI_Summary и NIR_Character_Summary."""
        try:
            fill_vuz_summary()  # Обновление таблицы VUZ_Summary
            fill_grnti_summary()  # Обновление таблицы GRNTI_Summary
            fill_nir_character_summary()  # Обновление таблицы NIR_Character_Summary
            print("Все сводные таблицы успешно обновлены.")
        except Exception as e:
            self.show_error_message(f"Ошибка при обновлении сводных таблиц: {e}")



    def hide_buttons(self):
        self.Tp_nir_redact_add_row_btn.hide()
        self.Tp_nir_redact_del_row_btn.hide()
        self.Tp_nir_redact_edit_row_btn.hide()
        self.Tp_nir_redact_filters_btn.hide()

    def show_buttons(self):
        self.Tp_nir_redact_add_row_btn.show()
        self.Tp_nir_redact_del_row_btn.show()
        self.Tp_nir_redact_edit_row_btn.show()
        self.Tp_nir_redact_filters_btn.show()



    def open_add_row_menu(self):
        """Сброс состояния и открытие меню добавления строки."""
        self.reset_add_row_menu()  # Сброс состояния меню
        self.fill_comboboxes_tp_nir_add_row_menu()  # Заполнение комбобоксов
        self.Tp_nir_add_row_menu_VUZcode_name_cmb.setCurrentIndex(-1)
        self.Tp_nir_add_row_menu_grntiNature_cmb.setCurrentIndex(-1)
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
        self.Tp_nir_add_row_menu_VUZcode_name_cmb.setCurrentIndex(-1)

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
        # Добавление элементов в комбобокс с пояснениями
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("П - Природное", "П")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("Р - Развивающее", "Р")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("Ф - Фундаментальное", "Ф")

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
        if int(planned_financing) <= 0:
            self.show_error_message("Плановое финансирование не может быть меньше или равно 0")
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
            row_position = model.rowCount()  # Получаем текущую позицию для новой строки
            model.insertRow(row_position)  # Вставляем новую строку

            # Заполняем новую строку данными
            for key, value in new_record.items():
                if value:  # Проверяем, что значение не пустое
                    model.setData(model.index(row_position, model.fieldIndex(key)), value)
                    print(f"Установлено: {key} = {value}")  # Отладка

            # Сохраняем изменения в базе данных
            if not model.submitAll():
                raise Exception(f"Ошибка сохранения данных: {model.lastError().text()}")

            # Обновляем модель
            model.select()  # Обновляем модель, чтобы отобразить изменения

            # Устанавливаем выделение на новую строку
            self.tableView.setCurrentIndex(model.index(row_position, 0))  # Устанавливаем выделение на новую строку
            self.stackedWidget.setCurrentIndex(0)  # Возвращаемся на основной экран
            #QMessageBox.information(self, "Успех", "Данные успешно сохранены.")


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
        if not conn.isOpen() and not conn.open():
            print("Ошибка: база данных не открыта.")
            return

        query = '''
                UPDATE Tp_fv
                SET 
                     "Плановое_финансирование" = (
                     SELECT SUM(Tp_nir."Плановое_финансирование")
                     FROM Tp_nir
                     WHERE Tp_fv."Код" = Tp_nir."Код"
                     GROUP BY Tp_nir."Код"
    )
        '''

        ql_query = QSqlQuery(conn)
        if not ql_query.exec(query):
            print(f"Ошибка при выполнении запроса: {ql_query.lastError().text()}")
            return
        else:
            print(f"Обновлено строк: {ql_query.numRowsAffected()}")

        # Перезагрузка модели
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

        # Установка сортировки по имени вуза (например, по столбцу "Сокращенное_имя")
        if table_name == 'Tp_nir':
            self.models[table_name].setSort(self.models[table_name].fieldIndex("Сокращенное_имя"),
                                            Qt.SortOrder.AscendingOrder)

        self.models[table_name].select()  # Обновление модели для применения сортировки

    def filter_by_cod_grnti(self):
        """Фильтрация по коду ГРНТИ."""
        str_cod = self.grnticode_txt.toPlainText().strip()

        # Регулярное выражение для проверки, что строка состоит из цифр и точек
        if not str_cod or not re.match(r'^[\d.]+$', str_cod):
            self.show_error_message(
                "Неправильное значение. Пожалуйста, введите численные значения, разделенные точками.")
            return

        # Получаем количество строк в модели
        row_count = self.models['Tp_nir'].rowCount()
        conditions = []

        for row in range(row_count):
            # Получаем значение из столбца "Коды_ГРНТИ"
            cods = self.models['Tp_nir'].data(self.models['Tp_nir'].index(row, 5))

            if cods is not None:
                cods = cods.split(';')  # Предполагаем, что коды разделены точкой с запятой
                cods = [cod.strip() for cod in cods]  # Убираем пробелы

                if len(cods) == 1:
                    # Если один код, применяем фильтр для одного кода
                    if cods[0].startswith(str_cod):
                        conditions.append(f'"Коды_ГРНТИ" = "{cods[0]}%;"')
                elif len(cods) == 2:
                    # Если два кода, применяем фильтр для двух кодов
                    if any(cod.startswith(str_cod) for cod in cods):
                        conditions.append(f'"Коды_ГРНТИ" LIKE "{str_cod}%"')


        if conditions:
            query = ' AND '.join(conditions)
            self.models['Tp_nir'].setFilter(query)
        else:
            self.models['Tp_nir'].setFilter("")  # Если нет условий, сбрасываем фильтр

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
            # Удаляем строку
            table_view.model().removeRow(selected_indexes[0].row())

            # Обновляем таблицу и сортируем по "Сокращенное имя"
            self.models['Tp_nir'].select()
            self.models['Tp_nir'].setSort(self.models['Tp_nir'].fieldIndex("Сокращенное_имя"),
                                          Qt.SortOrder.AscendingOrder)
            self.models['Tp_nir'].select()  # Применяем сортировку
            self.tableView.setModel(self.models['Tp_nir'])

    def save_data(self):
        """Сохранение данных."""
        for model in self.models.values():
            model.submitAll()


    def on_Tp_nir_redact_filters_close_btn_clicked(self):
        self.cancel(self.Tp_nir_add_row_menu)
        self.show_buttons()
        self.models['Tp_nir'].setFilter("")
        self.models['Tp_nir'].select()
        self.tableView.setModel(self.models['Tp_nir'])
        self.tableView.reset()
        self.tableView.show()







    def filter(self):
        self.show_menu(self.Tp_nir_add_row_menu, 3)
        self.hide_buttons()

        self.populate_initial_comboboxes()
        self.setup_combobox_signals()
        # Подключение сигналов для фильтрации
        self.grnticode_txt = self.findChild(QTextEdit, 'grnticode_txt')
        self.filter_by_grnticode_btn.clicked.connect(self.filter_by_cod_grnti)
        self.cancel_filtration_btn.clicked.connect(self.on_reset_filter)
        self.Tp_nir_redact_filters_close_btn.clicked.connect(self.on_Tp_nir_redact_filters_close_btn_clicked)

    def on_reset_filter(self):
        self.models['Tp_nir'].setFilter("")
        self.models['Tp_nir'].select()
        self.tableView_2.setModel(self.models['Tp_nir'])
        self.tableView_2.reset()
        self.tableView_2.show()

        # Очищаем комбобоксы
        self.vuz_cmb.clear()
        self.region_cmb.clear()
        self.city_cmb.clear()
        self.obl_cmb.clear()

        # Сброс значений в комбобоксах
        self.populate_initial_comboboxes()
        self.setup_combobox_signals()

        # Сброс флагов
        self.vuz_selected = False
        self.region_selected = False
        self.city_selected = False
        self.obl_selected = False

        # Сброс флагов для отслеживания изменений
        self.vuz_changed = False
        self.region_changed = False
        self.city_changed = False
        self.obl_changed = False

    def populate_combobox(self, column_name, combo_box, filters=None):
        """Заполнение конкретного комбобокса с учетом фильтра."""
        conn = sqlite3.connect(self.db_name)

        query = f'''
            SELECT DISTINCT VUZ."{column_name}"
            FROM VUZ
            JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
        '''

        if filters:
            # Убираем пустые фильтры и "Выберите..."
            filters = list(filter(lambda x: x and x != "Выберите...", filters))

            if filters:
                query += ' WHERE ' + ' AND '.join(filters)

        print("SQL-запрос для комбобокса:", query)  # Отладка

        df = conn.execute(query).fetchall()

        # Отладка: выводим извлеченные данные
        print(f"Данные для комбобокса {column_name}: {df}")

        # Проверяем, нужно ли добавлять "Выберите..."
        current_data = combo_box.currentText()
        # Добавляем "Выберите..." только если текущее значение - "Выберите..."
        if current_data is None:
            combo_box.clear()
            combo_box.addItem("Выберите...", None)  # Добавляем пустое значение

        for value in df:
            if value:
                combo_box.addItem(value[0])

        conn.close()

    def update_comboboxes(self):
        """Обновление значений в комбобоксах на основе выбранных значений."""
        # Получаем текущее значение выбранных комбобоксов
        vuz_selected = self.vuz_cmb.currentText()
        region_selected = self.region_cmb.currentText()
        city_selected = self.city_cmb.currentText()
        obl_selected = self.obl_cmb.currentText()

        print(
            f"Выбранные значения: VUZ={vuz_selected}, Регион={region_selected}, Город={city_selected}, Область={obl_selected}")

        if vuz_selected != "Выберите...":
            self.vuz_cmb.removeItem(0)  # Удаляем "Выберите..."
        else:
            self.vuz_cmb.addItem("Выберите...", None)  # Добавляем обратно, если выбрано "Выберите..."

        if region_selected != "Выберите...":
            self.region_cmb.removeItem(0)  # Удаляем "Выберите..."
        else:
            self.region_cmb.addItem("Выберите...", None)  # Добавляем обратно, если выбрано "Выберите..."

        if city_selected != "Выберите...":
            self.city_cmb.removeItem(0)  # Удаляем "Выберите..."
        else:
            self.city_cmb.addItem("Выберите...", None)  # Добавляем обратно, если выбрано "Выберите..."

        if obl_selected != "Выберите...":
            self.obl_cmb.removeItem(0)  # Удаляем "Выберите..."
        else:
            self.obl_cmb.addItem("Выберите...", None)  # Добавляем обратно, если выбрано "Выберите..."

        # Обновляем комбобоксы в зависимости от текущего выбора
        if vuz_selected != "Выберите..." and not self.vuz_changed:
            #self.vuz_cmb.removeItem(0)
            self.populate_combobox("Регион", self.region_cmb, [f'VUZ."Сокращенное_имя" = "{vuz_selected}"'])
            self.populate_combobox("Город", self.city_cmb, [f'VUZ."Сокращенное_имя" = "{vuz_selected}"'])
            self.populate_combobox("Область", self.obl_cmb, [f'VUZ."Сокращенное_имя" = "{vuz_selected}"'])

        if region_selected != "Выберите..." and not self.region_changed:
            #self.region_cmb.removeItem(0)
            self.populate_combobox("Сокращенное_имя", self.vuz_cmb, [f'VUZ."Регион" = "{region_selected}"'])
            self.populate_combobox("Город", self.city_cmb, [f'VUZ."Регион" = "{region_selected}"'])
            self.populate_combobox("Область", self.obl_cmb, [f'VUZ."Регион" = "{region_selected}"'])

        if city_selected != "Выберите..." and not self.city_changed:
            #self.city_cmb.removeItem(0)
            self.populate_combobox("Регион", self.region_cmb, [f'VUZ."Город" = "{city_selected}"'])
            self.populate_combobox("Сокращенное_имя", self.vuz_cmb, [f'VUZ."Город" = "{city_selected}"'])
            self.populate_combobox("Область", self.obl_cmb, [f'VUZ."Город" = "{city_selected}"'])

        if obl_selected != "Выберите..." and not self.obl_changed:
            #self.obl_cmb.removeItem(0)
            self.populate_combobox("Регион", self.region_cmb, [f'VUZ."Область" = "{obl_selected}"'])
            self.populate_combobox("Город", self.city_cmb, [f'VUZ."Область" = "{obl_selected}"'])
            self.populate_combobox("Сокращенное_имя", self.vuz_cmb, [f'VUZ."Область" = "{obl_selected}"'])

    def update_table(self):
        """Обновление таблицы Tp_nir на основе выбранных значений в комбобоксах."""
        filters = []

        # Проверяем, если выбран регион
        if self.region_cmb.currentText() != "Выберите...":
            filters.append(f'VUZ."Регион" = "{self.region_cmb.currentText()}"')


        # Проверяем, если выбран город
        if self.city_cmb.currentText() != "Выберите...":
            filters.append(f'VUZ."Город" = "{self.city_cmb.currentText()}"')


        # Проверяем, если выбрана область
        if self.obl_cmb.currentText() != "Выберите...":
            filters.append(f'VUZ."Область" = "{self.obl_cmb.currentText()}"')


        # Проверяем, если выбран ВУЗ
        if self.vuz_cmb.currentText() != "Выберите...":
            filters.append(f'VUZ."Сокращенное_имя" = "{self.vuz_cmb.currentText()}"')


        # Формируем SQL-запрос с JOIN
        query = '''
            SELECT Tp_nir.*
            FROM Tp_nir
            JOIN VUZ ON Tp_nir."Код" = VUZ."Код"
        '''

        # Если есть фильтры, добавляем их к запросу
        if filters:
            query += ' WHERE ' + ' AND '.join(filters)

        print()
        print("Применяемые фильтры:", filters)
        print("SQL-запрос:", query)

        # Создаем объект QSqlQuery и выполняем запрос
        ql_query = QSqlQuery()
        if not ql_query.exec(query):
            print(f"Ошибка при выполнении запроса: {ql_query.lastError().text()}")
            return

        # Устанавливаем модель с выполненным запросом
        model = QSqlQueryModel()
        model.setQuery(ql_query)

        self.tableView_2.setModel(model)

    def setup_combobox_signals(self):
        """Подключение сигналов для комбобоксов."""
        self.vuz_cmb.currentIndexChanged.connect(self.on_vuz_changed)
        self.region_cmb.currentIndexChanged.connect(self.on_region_changed)
        self.city_cmb.currentIndexChanged.connect(self.on_city_changed)
        self.obl_cmb.currentIndexChanged.connect(self.on_obl_changed)

    def on_vuz_changed(self):
        """Обработчик изменения VUZ."""
        if self.vuz_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.vuz_selected:
            self.vuz_selected = True
            self.update_comboboxes()
            self.update_table()

    def on_region_changed(self):
        """Обработчик изменения региона."""
        if self.region_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.region_selected:
            self.region_selected = True
            self.update_comboboxes()
            self.update_table()

    def on_city_changed(self):
        """Обработчик изменения города."""
        if self.city_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.city_selected:
            self.city_selected = True
            self.update_comboboxes()
            self.update_table()

    def on_obl_changed(self):
        """Обработчик изменения области."""
        if self.obl_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.obl_selected:
            self.obl_selected = True
            self.update_comboboxes()
            self.update_table()



    def populate_initial_comboboxes(self):
        """Заполнение комбобоксов существующими данными из связанных таблиц."""
        conn = sqlite3.connect(self.db_name)

        try:
            # Заполнение комбобокса VUZ
            query_vuz = '''
                SELECT DISTINCT VUZ."Сокращенное_имя"
                FROM VUZ
                JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
            '''
            df_vuz = conn.execute(query_vuz).fetchall()
            self.vuz_cmb.clear()  # Очистка перед заполнением
            self.vuz_cmb.addItem("Выберите...", None)  # Добавляем пустое значение
            for row in df_vuz:
                self.vuz_cmb.addItem(row[0])

            # Заполнение комбобокса Регион
            query_region = '''
                SELECT DISTINCT VUZ."Регион"
                FROM VUZ
                JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
            '''
            df_region = conn.execute(query_region).fetchall()
            self.region_cmb.clear()  # Очистка перед заполнением
            self.region_cmb.addItem("Выберите...", None)  # Добавляем пустое значение
            for row in df_region:
                self.region_cmb.addItem(row[0])  # row[0] содержит "Регион"

            # Заполнение комбобокса Город
            query_city = '''
                SELECT DISTINCT VUZ."Город"
                FROM VUZ
                JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
            '''
            df_city = conn.execute(query_city).fetchall()
            self.city_cmb.clear()  # Очистка перед заполнением
            self.city_cmb.addItem("Выберите...", None)  # Добавляем пустое значение
            for row in df_city:
                self.city_cmb.addItem(row[0])


            # Заполнение комбобокса Область
            query_obl = '''
                SELECT DISTINCT VUZ."Область"
                FROM VUZ
                JOIN Tp_nir ON VUZ."Код" = Tp_nir."Код"
            '''
            df_obl = conn.execute(query_obl).fetchall()
            self.obl_cmb.clear()  # Очистка перед заполнением
            self.obl_cmb.addItem("Выберите...", None)  # Добавляем пустое значение
            for row in df_obl:
                self.obl_cmb.addItem(row[0])  # row[0] содержит "Область"

        finally:
            conn.close()


        # Устанавливаем "Выберите..." как выбранное значение
        self.vuz_cmb.setCurrentIndex(0)  # Устанавливаем "Выберите..." как выбранное значение
        self.region_cmb.setCurrentIndex(0)
        self.city_cmb.setCurrentIndex(0)
        self.obl_cmb.setCurrentIndex(0)  # Устанавливаем "Выберите..." как выбранное значение


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())