import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QInputDialog,
                             QAbstractItemView, QComboBox, QTextEdit, QHeaderView, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QLabel, QWidget)
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

        self.is_updating = False  # Флаг для отслеживания обновления

        self.models['Tp_nir'].dataChanged.connect(self.on_tp_nir_data_changed)
        self.saved_filter_conditions = []  # Список для хранения условий фильтрации

    def on_tp_nir_data_changed(self):
        """Обработчик изменения данных в Tp_nir."""
        if not self.is_updating:
            self.is_updating = True  # Устанавливаем флаг обновления
            self.update_tp_fv()  # Обновляем первую модель
            self.update_summary_tables()  # Обновляем вторую модель
            self.is_updating = False  # Сбрасываем флаг обновления



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
            'NIR_Character_Summary': QSqlTableModel(self),
            'Order_table': QSqlTableModel(self)

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
        self.tableView_3.setSortingEnabled(True)
        self.tableView_3.horizontalHeader().setStretchLastSection(True)
        self.tableView_3.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableView_3.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.stackedWidget.setCurrentIndex(0)

        self.Tp_nir_redact.setVisible(False)


        # Подключение действий для отображения таблиц
        self.action_show_VUZ.triggered.connect(self.open_VUZ)
        self.action_show_Tp_nir.triggered.connect(self.open_Tp_nir)
        self.action_show_grntirub.triggered.connect(self.open_grntirub)
        self.action_show_Tp_fv.triggered.connect(self.open_Tp_fv)
        self.tableView_2.setModel(self.models['Tp_nir'])  # New

        # # Подключение действий для отображения таблиц
        # self.action_show_VUZ.triggered.connect(lambda: self.table_show('VUZ'))
        # self.action_show_Tp_nir.triggered.connect(lambda: self.table_show('Tp_nir'))
        # self.action_show_grntirub.triggered.connect(lambda: self.table_show('grntirub'))
        # self.action_show_Tp_fv.triggered.connect(lambda: self.table_show('Tp_fv'))
        # self.tableView_2.setModel(self.models['Tp_nir'])  # New

        self.po_VUZ.triggered.connect(self.open_analysis_menu_po_VUZ)
        self.po_rubrikam.triggered.connect(self.open_analysis_menu_po_rubrikam)
        self.po_character.triggered.connect(self.open_analysis_menu_po_character)
        #
        # self.po_rubrikam.triggered.connect(lambda: self.table_show('GRNTI_Summary'))
        # self.po_character.triggered.connect(lambda: self.table_show('NIR_Character_Summary'))
        # self.po_VUZ.triggered.connect(lambda: self.table_show('VUZ_Summary'))

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
        self.grnticode_cmb = self.findChild(QComboBox, 'grnticode_cmb')
        self.filter_by_grnticode_btn = self.findChild(QPushButton, 'filter_by_grnticode_btn')

        self.save_filter_cod_btn = self.findChild(QPushButton, 'save_filter_cod_btn')
        self.cancel_filter_cod_btn = self.findChild(QPushButton, 'cancel_filter_cod_btn')

        self.cancel_filter_complex_btn = self.findChild(QPushButton, 'cancel_filter_complex_btn')
        self.save_filter_complex_btn = self.findChild(QPushButton, 'save_filter_complex_btn')

        self.Tp_nir_redact_filters_close_btn = self.findChild(QPushButton, 'Tp_nir_redact_filters_close_btn')

        #Анализ

       #self.apply_filter_btn.clicked.connect(self.apply_saved_filters)
        self.wid = self.findChild(QWidget, "widget")

        #Выпуск распоряжений
        self.current_order.triggered.connect(self.on_current_order_clicked)

        self.calculate_btn.clicked.connect(self.on_calculate_btn_clicked)
        self.save_project_btn.clicked.connect(self.on_save_project_btn_clicked)
        self.accept_order_btn.clicked.connect(self.on_accept_order_btn_clicked)
        self.cancel_order_btn.clicked.connect(self.on_cancel_order_btn_clicked)
        self.clean_btn.clicked.connect(self.on_clean_btn_clicked)


        self.sum_first_lineedit = self.findChild(QLineEdit, 'sum_first_lineedit')
        self.sum_second_lbl = self.findChild(QLabel, 'sum_second_lbl')
        self.ordered_percent_first_lbl = self.findChild(QLabel, 'ordered_percent_first_lbl')
        self.ordered_percent_second_lineedit = self.findChild(QLineEdit, 'ordered_percent_second_lineedit')

        self.plan_fin_lbl = self.findChild(QLabel, 'plan_fin_lbl')
        self.fact_fin_lbl = self.findChild(QLabel, 'fact_fin_lbl')
        self.ordered_fin_percent_lbl = self.findChild(QLabel, 'ordered_fin_percent_lbl')

    def on_current_order_clicked(self):
        self.hide_buttons()
        self.stackedWidget.setCurrentIndex(4)
        value = self.get_sum_value_by_column("Плановое_финансирование")
        self.table_show('Order_table')
        self.plan_fin_lbl.setText(str(value))
        self.fact_fin_lbl.setText('0')
        self.ordered_fin_percent_lbl.setText('0')

    def on_calculate_btn_clicked(self):
        # Проверяем, что только одно из полей заполнено
        if self.sum_first_lineedit.text() and self.ordered_percent_second_lineedit.text():
            self.show_error_message("Заполните только одно из полей: 'Сумма' или 'Процент'.")
            return

        # Проверяем первое поле
        if self.sum_first_lineedit.text():
            if not self.validate_lineedit(self.sum_first_lineedit):
                return

            value = int(self.sum_first_lineedit.text())
            sum_value = int(self.plan_fin_lbl.text())

            if value > sum_value:
                self.show_error_message("Введенное значение не может быть больше планового финансирования")
                self.reset_first_lineedit()
                return

            res = round(value * 100 / sum_value, 1)
            self.ordered_percent_first_lbl.setText(str(res))

        # Проверяем второе поле
        elif self.ordered_percent_second_lineedit.text():
            if not self.validate_lineedit(self.ordered_percent_second_lineedit):
                return  # Если валидация не прошла, выходим из метода

            percent_val = int(self.ordered_percent_second_lineedit.text())
            if percent_val > 100:
                self.show_error_message("Нельзя вводить значение больше 100%")
                self.reset_second_lineedit()
                return

            sum_value = int(self.plan_fin_lbl.text())
            res = round(percent_val * sum_value / 100, 1)
            self.sum_second_lbl.setText(str(res))



    def validate_lineedit(self, lineedit):
        """Проверяет, что значение в lineedit является числом и не пустое."""
        text = lineedit.text()
        if text == '' or not text.isdigit():
            self.show_error_message("В ячейках должны быть только численные значения")
            return False
        return True

    def reset_first_lineedit(self):
        self.sum_first_lineedit.clear()
        self.ordered_percent_first_lbl.clear()

    def reset_second_lineedit(self):
        self.ordered_percent_second_lineedit.clear()
        self.sum_second_lbl.clear()




    def on_save_project_btn_clicked(self):
        pass

    def on_accept_order_btn_clicked(self):
        pass

    def on_cancel_order_btn_clicked(self):
        #self.show_buttons()
        self.stackedWidget.setCurrentIndex(0)
        #добавить отмену уже рассчитанных факт. фин.

    def on_clean_btn_clicked(self):
        self.reset_first_lineedit()
        self.reset_second_lineedit()

    def get_sum_value_by_column(self,column_name):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(f'''SELECT SUM({column_name}) FROM Tp_fv''')
        res = c.fetchone()
        sum_value = res[0] if res[0] is not None else 0
        conn.commit()
        conn.close()
        return sum_value


    #
    # def table_show(self, table_name):
    #     """Отображение таблицы."""
    #     #self.hide_buttons()
    #     if table_name == 'Tp_nir':
    #         self.show_buttons()
    #         self.models[table_name].setSort(self.models[table_name].fieldIndex("Сокращенное_имя"),
    #                                         Qt.SortOrder.AscendingOrder)
    #     if table_name == 'Order_table':
    #         self.tableView_3.setModel(self.models[table_name])
    #         self.models[table_name].setSort(self.models[table_name].fieldIndex("Сокращенное_имя"),
    #                                         Qt.SortOrder.AscendingOrder)
    #     if table_name.endswith('Summary'):
    #         self.tableView_2.setModel(self.models[table_name])
    #     else:
    #         self.tableView.setModel(self.models[table_name])
    #     self.models[table_name].select()


    def table_show(self, table_name):
        """Отображение таблицы."""
        self.tableView.setModel(self.models[table_name])

    def open_VUZ(self):
        self.stackedWidget.setCurrentIndex(0)
        self.Tp_nir_redact.setVisible(False)
        self.table_show('VUZ')

    def open_Tp_nir(self):
        self.stackedWidget.setCurrentIndex(0)
        self.Tp_nir_redact.setVisible(True)
        self.table_show('Tp_nir')

    def open_Tp_fv(self):
        self.stackedWidget.setCurrentIndex(0)
        self.Tp_nir_redact.setVisible(False)
        self.table_show('Tp_fv')

    def open_grntirub(self):
        self.stackedWidget.setCurrentIndex(0)
        self.Tp_nir_redact.setVisible(False)
        self.table_show('grntirub')

    def table_show_3(self, table_name):
        """Отображение таблицы."""
        self.tableView_3.setModel(self.models[table_name])

    def table_show_2(self, table_name):
        """Отображение таблицы."""
        self.tableView_2.setModel(self.models[table_name])

    def open_analysis_menu_po_VUZ(self):
        self.stackedWidget.setCurrentIndex(3)
        self.Tp_nir_redact.setVisible(False)
        self.wid.setVisible(False)
        self.table_show_2('VUZ_Summary')

    def open_analysis_menu_po_rubrikam(self):
        self.stackedWidget.setCurrentIndex(3)
        self.Tp_nir_redact.setVisible(False)
        self.wid.setVisible(False)
        self.table_show_2('GRNTI_Summary')

    def open_analysis_menu_po_character(self):
        self.stackedWidget.setCurrentIndex(3)
        self.Tp_nir_redact.setVisible(False)
        self.wid.setVisible(False)

        self.table_show_2('NIR_Character_Summary')


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
        self.tableView_2.setModel(self.models['VUZ_Summary'])  # Устанавливаем модель в таблицу
        print("Применены сохраненные условия фильтрации к VUZ_Summary.")

    def update_summary_tables(self):
        """Обновление таблиц VUZ_Summary, GRNTI_Summary и NIR_Character_Summary."""
        if self.is_updating:
            return  # Если уже происходит обновление, выходим

        try:
            self.is_updating = True  # Устанавливаем флаг обновления
            fill_vuz_summary()  # Обновление таблицы VUZ_Summary
            fill_grnti_summary()  # Обновление таблицы GRNTI_Summary
            fill_nir_character_summary()  # Обновление таблицы NIR_Character_Summary
            print("Все сводные таблицы успешно обновлены.")
        except Exception as e:
            self.show_error_message(f"Ошибка при обновлении сводных таблиц: {e}")
        finally:
            self.is_updating = False  # Сбрасываем флаг обновления



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
        grnti_number = self.Tp_nir_add_row_menu_grntiNumber_txt.toPlainText().strip()
        grnti_nature = self.Tp_nir_add_row_menu_grntiNature_cmb.currentData()
        grnti_head = self.Tp_nir_add_add_row_menu_grntiHead_txt.toPlainText().strip()
        grnti_code = self.Tp_nir_add_row_menu_grntiCode_txt.toPlainText().strip()
        grnti_name = self.Tp_nir_add_row_menu_grntiName_txt.toPlainText().strip()
        grnti_head_post = self.Tp_nir_add_row_menu_grntiHeadPost_txt.toPlainText().strip()
        planned_financing = self.Tp_nir_add_row_menu_plannedFinancing_txt.toPlainText().strip()
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
        query = QSqlQuery()
        query.prepare(existing_record_query)
        query.addBindValue(vuz_code)
        query.addBindValue(grnti_number)

        if not query.exec():
            self.show_error_message("Ошибка при выполнении запроса: " + query.lastError().text())
            return

        if query.next():
            existing_count = query.value(0)

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

        #print("Данные для сохранения:", new_record)

        try:
            # Получаем модель и добавляем новую строку
            model = self.models['Tp_nir']
            row_position = model.rowCount()  # Получаем текущую позицию для новой строки
            model.insertRow(row_position)  # Вставляем новую строку

            # Заполняем новую строку данными
            for key, value in new_record.items():
                if value:  # Проверяем, что значение не пустое
                    model.setData(model.index(row_position, model.fieldIndex(key)), value)
                    #print(f"Установлено: {key} = {value}")  # Отладка

            # Сохраняем изменения в базе данных
            if not model.submitAll():
                raise Exception(f"Ошибка сохранения данных: {model.lastError().text()}")

            # Обновляем модель
            # Обновляем модель
            model.select()  # Обновляем модель, чтобы отобразить изменения

            # Находим новый индекс строки с совпадением vuz_code и grnti_number
            row_to_scroll = None
            #print(f"Ищем запись с Код = {vuz_code} и Номер = {grnti_number}")  # Отладка
            for row in range(model.rowCount()):
                current_code = model.data(model.index(row, model.fieldIndex('Код')))
                current_number = model.data(model.index(row, model.fieldIndex('Номер')))
                #print(f"Проверяем строку {row}: Код = {current_code}, Номер = {current_number}")  # Отладка
                if (str(current_code).strip() == str(vuz_code).strip() and str(current_number).strip() == str(grnti_number).strip()):
                    row_to_scroll = row
                    break

            # Прокручиваем до нужной строки и выделяем её
            if row_to_scroll is not None:
                self.tableView.scrollTo(model.index(row_to_scroll, 0))
                self.tableView.setCurrentIndex(model.index(row_to_scroll, 0))  # Устанавливаем выделение на строку
            else:
                self.show_error_message("Не удалось найти добавленную запись.")
            self.stackedWidget.setCurrentIndex(0)  # Возвращаемся на основной экран

        except Exception as e:
            self.show_error_message(f"Ошибка при сохранении данных: {e}")
            print(f"Ошибка: {e}")

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

        # Обновление планового финансирования
        query_plan = '''
                UPDATE Tp_fv
                SET 
                    "Плановое_финансирование" = (
                        SELECT SUM(Tp_nir."Плановое_финансирование")
                        FROM Tp_nir
                        WHERE Tp_fv."Код" = Tp_nir."Код"
                        GROUP BY Tp_nir."Код"
                    )
                WHERE EXISTS (
                    SELECT 1
                    FROM Tp_nir
                    WHERE Tp_fv."Код" = Tp_nir."Код"
                )
        '''

        ql_query = QSqlQuery(conn)
        if not ql_query.exec(query_plan):
            print(
                f"Ошибка при выполнении запроса на обновление планового финансирования: {ql_query.lastError().text()}")
            return
        else:
            print(f"Обновлено строк: {ql_query.numRowsAffected()}")

        query_count = '''
                UPDATE Tp_fv
                SET 
                    "Количество_НИР" = (
                        SELECT COUNT(Tp_nir."Номер")
                        FROM Tp_nir
                        WHERE Tp_fv."Код" = Tp_nir."Код"
                        GROUP BY Tp_nir."Код"
                    )
                WHERE EXISTS (
                    SELECT 1
                    FROM Tp_nir
                    WHERE Tp_fv."Код" = Tp_nir."Код"
                )
        '''

        if not ql_query.exec(query_count):
            print(f"Ошибка при выполнении запроса на обновление количества НИР: {ql_query.lastError().text()}")
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

    # def table_show(self, table_name):
    #     """Отображение таблицы."""
    #     self.tableView.setModel(self.models[table_name])
    #
    #     # Установка сортировки по имени вуза (например, по столбцу "Сокращенное_имя")
    #     if table_name == 'Tp_nir':
    #         self.models[table_name].setSort(self.models[table_name].fieldIndex("Сокращенное_имя"),
    #                                         Qt.SortOrder.AscendingOrder)
    #
    #     self.models[table_name].select()  # Обновление модели для применения сортировки

    def filter_by_cod_grnti(self):
        """Фильтрация по коду ГРНТИ."""
        if self.grnticode_cmb.currentIndex() == -1:
            self.show_error_message("Пожалуйста, выберите код ГРНТИ из комбобокса.")
            return

        str_cod = str(self.grnticode_cmb.currentData())
        print(str_cod)

        if not str_cod:
            self.show_error_message("Пожалуйста, выберите код ГРНТИ из комбобокса.")
            return

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
                    if all(cod.startswith(str_cod) for cod in cods):
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
        self.wid.setVisible(True)

        # Подключение сигналов для фильтрации

        self.grnticode_cmb.addItem("Выберите...", None)
        grnti_items = grnti_to_cmb()
        # Заполняем комбобокс
        for code, display_text in grnti_items:
            self.grnticode_cmb.addItem(display_text, code)


        self.filter_by_grnticode_btn.clicked.connect(self.filter_by_cod_grnti)

        self.save_filter_cod_btn.clicked.connect(self.save_filter_grnti)
        self.cancel_filter_cod_btn.clicked.connect(self.on_reset_filter_by_grnti_code)

        self.cancel_filter_complex_btn.clicked.connect(self.on_reset_filter)
        self.save_filter_complex_btn.clicked.connect(self.save_filter_complex)

        self.Tp_nir_redact_filters_close_btn.clicked.connect(self.on_Tp_nir_redact_filters_close_btn_clicked)



    def on_reset_filter_by_grnti_code(self):
        pass

    def save_filter_grnti(self):
        pass

    def save_filter_complex(self):
        pass

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

        self.vuz_selected = False
        self.region_selected = False
        self.city_selected = False
        self.obl_selected = False

        # Инициализация флагов для отслеживания изменений
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
        if current_data == "Выберите...":
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

        print(f"Выбранные значения: VUZ={vuz_selected}, Регион={region_selected}, Город={city_selected}, Область={obl_selected}")

        # Обновляем комбобоксы в зависимости от текущего выбора
        if vuz_selected != "Выберите...":
            self.populate_combobox("Регион", self.region_cmb, [f'VUZ."Сокращенное_имя" = "{vuz_selected}"'])
            self.populate_combobox("Город", self.city_cmb, [f'VUZ."Сокращенное_имя" = "{vuz_selected}"'])
            self.populate_combobox("Область", self.obl_cmb, [f'VUZ."Сокращенное_имя" = "{vuz_selected}"'])

        if region_selected != "Выберите...":
            self.populate_combobox("Сокращенное_имя", self.vuz_cmb, [f'VUZ."Регион" = "{region_selected}"'])
            self.populate_combobox("Город", self.city_cmb, [f'VUZ."Регион" = "{region_selected}"'])
            self.populate_combobox("Область", self.obl_cmb, [f'VUZ."Регион" = "{region_selected}"'])

        if city_selected != "Выберите...":
            self.populate_combobox("Регион", self.region_cmb, [f'VUZ."Город" = "{city_selected}"'])
            self.populate_combobox("Сокращенное_имя", self.vuz_cmb, [f'VUZ."Город" = "{city_selected}"'])
            self.populate_combobox("Область", self.obl_cmb, [f'VUZ."Город" = "{city_selected}"'])

        if obl_selected != "Выберите...":
            self.populate_combobox("Регион", self.region_cmb, [f'VUZ."Область" = "{obl_selected}"'])
            self.populate_combobox("Город", self.city_cmb, [f'VUZ."Область" = "{obl_selected}"'])
            self.populate_combobox("Сокращенное_имя", self.vuz_cmb, [f'VUZ."Область" = "{obl_selected}"'])

        self.update_table()

        self.vuz_selected = False
        self.region_selected = False
        self.city_selected = False
        self.obl_selected = False

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