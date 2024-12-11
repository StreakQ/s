import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QInputDialog,
                             QAbstractItemView, QComboBox, QTextEdit, QHeaderView, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QLineEdit)
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

        self.saved_filter_grnti_conditions = []  # Условия фильтрации по коду ГРНТИ
        self.saved_filter_complex_conditions = []

    def on_tp_nir_data_changed(self):
        """Обработчик изменения данных в Tp_nir."""
        self.update_tp_fv()  # Обновляем первую модель
        self.update_summary_tables()  # Обновляем вторую модель

    def connect_db(self):
        """Подключение к базе данных."""
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.db_name)
        #self.db.setConnectOptions("PRAGMA busy_timeout = 3000")
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
        self.tableView_4.setSortingEnabled(True)
        self.tableView_4.horizontalHeader().setStretchLastSection(True)
        self.tableView_4.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableView_4.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.stackedWidget.setCurrentIndex(0)

        self.Tp_nir_redact.setVisible(False)

        # Подключение действий для отображения таблиц
        self.action_show_VUZ.triggered.connect(self.open_VUZ)
        self.action_show_Tp_nir.triggered.connect(self.open_Tp_nir)
        self.action_show_grntirub.triggered.connect(self.open_grntirub)
        self.action_show_Tp_fv.triggered.connect(self.open_Tp_fv)
        self.tableView_2.setModel(self.models['Tp_nir'])  # New

        self.po_VUZ.triggered.connect(self.open_analysis_menu_po_VUZ)
        self.po_rubrikam.triggered.connect(self.open_analysis_menu_po_rubrikam)
        self.po_character.triggered.connect(self.open_analysis_menu_po_character)

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

        # Анализ
        self.apply_filter_btn = self.findChild(QPushButton, 'apply_filter_btn')
        self.apply_filter_btn.clicked.connect(self.apply_saved_filters)
        self.wid = self.findChild(QWidget, "widget")
        self.refund_to_filters_btn = self.findChild(QPushButton,'refund_to_filters_btn')
        self.refund_to_filters_btn.clicked.connect(self.on_refund_to_filters_btn_clicked)

        # Выпуск распоряжений
        self.current_order.triggered.connect(self.on_current_order_clicked)

        self.calculate_btn.clicked.connect(self.on_calculate_btn_clicked)
        self.save_project_btn.clicked.connect(self.on_save_project_btn_clicked)
        self.accept_order_btn.clicked.connect(self.on_accept_order_btn_clicked)
        self.cancel_order_btn.clicked.connect(self.on_cancel_order_btn_clicked)
        self.clean_btn.clicked.connect(self.on_clean_btn_clicked)
        self.distribute_to_vuz_btn.clicked.connect(self.on_distribute_to_vuz_clicked)


        self.sum_first_lineedit = self.findChild(QLineEdit, 'sum_first_lineedit')
        self.sum_second_lbl = self.findChild(QLabel, 'sum_second_lbl')
        self.ordered_percent_first_lbl = self.findChild(QLabel, 'ordered_percent_first_lbl')
        self.ordered_percent_second_lineedit = self.findChild(QLineEdit, 'ordered_percent_second_lineedit')

        self.plan_fin_lbl = self.findChild(QLabel, 'plan_fin_lbl')
        self.fact_fin_lbl = self.findChild(QLabel, 'fact_fin_lbl')
        self.ordered_fin_percent_lbl = self.findChild(QLabel, 'ordered_fin_percent_lbl')

    def on_refund_to_filters_btn_clicked(self):
        self.show_buttons()
        self.stackedWidget.setCurrentIndex(3)
        self.Tp_nir_redact.setVisible(True)
        self.wid.setVisible(True)

    def on_current_order_clicked(self):
        self.hide_buttons()
        self.stackedWidget.setCurrentIndex(4)
        value = self.get_sum_value_by_column("Плановое_финансирование","Tp_fv")
        self.table_show('Order_table')
        self.plan_fin_lbl.setText(str(value))
        self.fact_fin_lbl.setText('0')
        self.ordered_fin_percent_lbl.setText('0')

    def on_calculate_btn_clicked(self):
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
        # self.show_buttons()
        self.stackedWidget.setCurrentIndex(0)
        self.open_Tp_nir()
        self.show_buttons()
        # добавить отмену уже рассчитанных факт. фин.

    def on_clean_btn_clicked(self):
        self.reset_first_lineedit()
        self.reset_second_lineedit()

    def on_distribute_to_vuz_clicked(self):
        if self.ordered_percent_first_lbl is not None and self.ordered_percent_first_lbl.text() != '':
            val = float(self.ordered_percent_first_lbl.text())
        elif self.ordered_percent_second_lineedit is not None and self.ordered_percent_second_lineedit.text() != '':
            val = float(self.ordered_percent_second_lineedit.text())
        else:
            self.show_error_message("Нет рассчитанных сумм")
            return

        conn = QSqlDatabase.database()
        if not conn.isOpen() and not conn.open():
            print("Ошибка: база данных не открыта.")
            return

        try:
            conn.transaction()
            fill_order_table(val,conn)
            self.update_labels()
            self.update_tp_fv()
            self.update_summary_tables()
            conn.commit()
            self.models['Order_table'].setFilter("")
            self.models['Order_table'].select()
        except Exception as e:
            print(f"Ошибка при распределении финансирования: {e}")
            conn.rollback()
        finally:
            conn.close()



        #TODO:также отображаем Order_table в tableView_3

    def update_labels(self):
        self.fact_sum = 0
        self.start_plan_sum = int(self.plan_fin_lbl.text())

        self.fact_sum += self.get_sum_value_by_column("Сумма_фактического_финансирования","Order_table")

        self.plan_sum = int(self.plan_fin_lbl.text()) - self.fact_sum

        self.percent_distrib_fact_sum = 0
        self.percent_distrib_fact_sum = self.plan_sum * 100 /self.start_plan_sum

        self.plan_fin_lbl.setText(str(self.plan_sum))
        self.fact_fin_lbl.setText(str(self.fact_sum))
        self.ordered_fin_percent_lbl.setText(str(self.percent_distrib_fact_sum))


    def get_sum_value_by_column(self, column_name,table_name):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(f'''SELECT SUM({column_name}) FROM {table_name}''')
        res = c.fetchone()
        sum_value = res[0] if res[0] is not None else 0
        conn.commit()
        conn.close()
        return sum_value

    def table_show(self, table_name):
        """Отображение таблицы."""
        self.tableView.setModel(self.models[table_name])

    def open_VUZ(self):
        self.stackedWidget.setCurrentIndex(0)
        self.Tp_nir_redact.setVisible(False)
        self.apply_filter_btn.setVisible(False)

        self.table_show('VUZ')

    def open_Tp_nir(self):
        self.stackedWidget.setCurrentIndex(0)
        self.apply_filter_btn.setVisible(False)
        self.Tp_nir_redact.setVisible(True)
        self.show_buttons()
        self.table_show('Tp_nir')

    def open_Tp_fv(self):
        self.stackedWidget.setCurrentIndex(0)
        self.Tp_nir_redact.setVisible(False)
        self.apply_filter_btn.setVisible(False)

        self.table_show('Tp_fv')

    def open_grntirub(self):
        self.stackedWidget.setCurrentIndex(0)
        self.Tp_nir_redact.setVisible(False)
        self.apply_filter_btn.setVisible(False)
        self.table_show('grntirub')

    def table_show_4(self, table_name):
        """Отображение таблицы."""
        self.tableView_4.setModel(self.models[table_name])

    def table_show_2(self, table_name):
        """Отображение таблицы."""
        self.tableView_2.setModel(self.models[table_name])

    def open_analysis_menu_po_VUZ(self):
        self.stackedWidget.setCurrentIndex(5)
        self.Tp_nir_redact.setVisible(False)
        self.wid.setVisible(False)
        self.apply_filter_btn.setVisible(True)
        self.table_show_4('VUZ_Summary')

    def open_analysis_menu_po_rubrikam(self):
        self.stackedWidget.setCurrentIndex(5)
        self.Tp_nir_redact.setVisible(False)
        self.wid.setVisible(False)
        self.apply_filter_btn.setVisible(False)
        self.refund_to_filters_btn.setVisible(False)
        self.table_show_4('GRNTI_Summary')

    def open_analysis_menu_po_character(self):
        self.stackedWidget.setCurrentIndex(5)
        self.Tp_nir_redact.setVisible(False)
        self.wid.setVisible(False)
        self.apply_filter_btn.setVisible(False)
        self.refund_to_filters_btn.setVisible(False)

        self.table_show_4('NIR_Character_Summary')

    def save_filter_conditions(self):
        """Сохранение условий фильтрации по коду ГРНТИ."""
        str_cod = self.grnticode_txt.toPlainText().strip()
        if str_cod:
            self.saved_filter_conditions.append(str_cod)
            print(f"Сохранено условие фильтрации: {str_cod}")
        else:
            self.show_error_message("Введите код ГРНТИ для сохранения условия фильтрации.")

    def update_summary_tables(self):
        """Обновление таблиц VUZ_Summary, GRNTI_Summary и NIR_Character_Summary."""
        conn = QSqlDatabase.database()  # Используем подключение к базе данных
        if not conn.isOpen() and not conn.open():
            print("Ошибка: база данных не открыта.")
            return

        try:
            conn.transaction()  # Начинаем транзакцию
            fill_vuz_summary()  # Обновление таблицы VUZ_Summary
            fill_grnti_summary()  # Обновление таблицы GRNTI_Summary
            fill_nir_character_summary()  # Обновление таблицы NIR_Character_Summary
            conn.commit()  # Подтверждаем транзакцию
            print("Все сводные таблицы успешно обновлены.")
        except Exception as e:
            conn.rollback()  # Откат транзакции в случае ошибки
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
        self.Tp_nir_add_row_menu_grntiNature_cmb.addItem("П - Прикладное исследование")
        self.Tp_nir_add_row_menu_grntiNature_cmb.setItemData(0, "П")
        self.Tp_nir_add_row_menu_grntiNature_cmb.addItem("Р - Экспериментальная разработка")
        self.Tp_nir_add_row_menu_grntiNature_cmb.setItemData(1, "Р")
        self.Tp_nir_add_row_menu_grntiNature_cmb.addItem("Ф - Фундаментальное исследование")
        self.Tp_nir_add_row_menu_grntiNature_cmb.setItemData(2, "Ф")

        print("Заполнен комбобокс характера")  # Отладка

    def fill_comboboxes_tp_nir_edit_row_menu(self):
        """Заполнение комбобоксов в меню редактирования строки."""
        self.Tp_nir_edit_row_menu_grntiNature_cmb.clear()

        # Заполнение комбобокса для характера
        # Добавление элементов в комбобокс с пояснениями
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("П - Прикладное исследование", "П")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("Р - Экспериментальная разработка", "Р")
        self.Tp_nir_edit_row_menu_grntiNature_cmb.addItem("Ф - Фундаментальное исследование", "Ф")

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
            print(f"row_pos{ row_position}")
            # Устанавливаем выделение на новую строку
            self.tableView.setModel(model)  # Устанавливаем модель в представление
            self.tableView.setCurrentIndex(model.index(row_position, 0))  # Устанавливаем выделение на новую строку
            self.stackedWidget.setCurrentIndex(0)  # Возвращаемся на основной экран

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

        try:
            # Проверяем количество строк в Tp_nir
            count_query = "SELECT COUNT(*) FROM Tp_nir"
            count_result = QSqlQuery(conn)
            if not count_result.exec(count_query):
                print(f"Ошибка при выполнении запроса: {count_result.lastError().text()}")
                return

            if count_result.next():
                count = count_result.value(0)
                print(f"Количество строк в Tp_nir перед обновлением: {count}")

            # Начинаем транзакцию
            if not conn.transaction():
                print("Ошибка: не удалось начать транзакцию.")
                return

            # Обновление планового финансирования
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
                conn.rollback()  # Откат транзакции в случае ошибки
                return

            print(f"Обновлено строк: {ql_query.numRowsAffected()}")

            # Обновление количества НИР
            query_count = '''
                UPDATE Tp_fv
                SET 
                    "Количество_НИР" = (
                        SELECT COUNT(Tp_nir."Номер")
                        FROM Tp_nir WHERE Tp_fv."Код" = Tp_nir."Код"
                        GROUP BY Tp_nir."Код"
                    )
            '''
            ql_query = QSqlQuery(conn)
            if not ql_query.exec(query_count):
                print(f"Ошибка при выполнении запроса на обновление количества НИР: {ql_query.lastError().text()}")
                conn.rollback()  # Откат транзакции в случае ошибки
                return
            print(f"Обновлено строк: {ql_query.numRowsAffected()}")

            print("Таблица Tp_fv обновлена на основе изменений в Tp_nir.")
            # Перезагрузка модели
            self.setup_models()
            conn.commit()

        except Exception as e:
            print(f"Ошибка: {e}")
            conn.rollback()  # Откат транзакции в случае ошибки
        finally:
            self.is_updating = False  # Сбрасываем флаг обновления
            conn.close()

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

    def filter_by_cod_grnti(self):
        """Фильтрация по коду ГРНТИ."""
        str_cod = str(self.grnticode_cmb.currentData())
        print("Выбранный код ГРНТИ:", str_cod)

        initial_row_count = self.models['Tp_nir'].rowCount()
        print("Количество строк до фильтрации:", initial_row_count)
        conditions = []
        first_two_digits_set = set()  # Множество для хранения первых двух цифр кодов

        # Сначала собираем все первые две цифры кодов
        for row in range(initial_row_count):
            cods = self.models['Tp_nir'].data(self.models['Tp_nir'].index(row, 5))
            if cods is not None:
                cods = cods.split(';')
                cods = [cod.strip() for cod in cods if cod.strip()]
                for cod in cods:
                    if len(cod) >= 2:  # Проверяем, что код достаточно длинный
                        first_two_digits_set.add(cod[:2])  # Добавляем первые две цифры в множество

        # Проверяем, содержится ли str_cod в множестве первых двух цифр
        if str_cod not in first_two_digits_set:
            self.show_error_message("Код ГРНТИ не найден в таблице.")
            return  # Выходим из функции, если код не найден

        # Если код найден, продолжаем фильтрацию
        for row in range(initial_row_count):
            cods = self.models['Tp_nir'].data(self.models['Tp_nir'].index(row, 5))
            if cods is not None:
                cods = cods.split(';')
                cods = [cod.strip() for cod in cods if cod.strip()]

                if len(cods) == 1:
                    if cods[0].startswith(str_cod):
                        conditions.append(f'"Коды_ГРНТИ" LIKE "{str_cod}%"')
                elif len(cods) == 2:
                    if all(cod.startswith(str_cod) for cod in cods):
                        conditions.append(f'"Коды_ГРНТИ" LIKE "{str_cod}%"')

        if conditions:
            query = ' AND '.join(conditions)
            print("Формируемый запрос:", query)
            self.models['Tp_nir'].setFilter(query)
            self.models['Tp_nir'].select()

            filtered_row_count = self.models['Tp_nir'].rowCount()
            print("Количество строк после фильтрации:", filtered_row_count)

            if filtered_row_count == initial_row_count:
                self.show_error_message("Нет записей с таким кодом ГРНТИ в таблице.")
                self.models['Tp_nir'].setFilter("")
                self.models['Tp_nir'].select()
        else:
            self.models['Tp_nir'].setFilter("")
            self.models['Tp_nir'].select()

        self.tableView.setModel(self.models['Tp_nir'])
        self.tableView.reset()
        self.tableView.show()

        self.filter_by_grnticode_btn.setEnabled(False)
        self.grnticode_cmb.setEnabled(False)
        self.menu_1.setEnabled(False)

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
        self.models['Tp_nir'].setFilter("")  # Сброс фильтров
        self.models['Tp_nir'].select()  # Обновление модели
        self.tableView_2.setModel(self.models['Tp_nir'])  # Убедитесь, что модель установлена
        self.tableView_2.reset()  # Сброс таблицы
        self.tableView_2.show()  # Показать таблицу

    def clear_and_fill_grnticmb(self):
        self.grnticode_cmb.clear()
        self.grnticode_cmb.addItem("Выберите...", None)
        grnti_items = grnti_to_cmb()

        for display_text in grnti_items:
            code, text = display_text.split(" - ")
            self.grnticode_cmb.addItem(display_text, code)

    def reset_filter_state(self):
        """Сброс состояния фильтров."""
        # Сбрасываем значения комбобоксов
        self.clear_and_fill_grnticmb()
        self.vuz_cmb.setCurrentIndex(0)
        self.region_cmb.setCurrentIndex(0)
        self.city_cmb.setCurrentIndex(0)
        self.obl_cmb.setCurrentIndex(0)  # Отключаем кнопки фильтрации
        self.filter_by_grnticode_btn.setEnabled(True)
        self.save_filter_cod_btn.setEnabled(True)
        self.cancel_filter_cod_btn.setEnabled(True)
        self.cancel_filter_complex_btn.setEnabled(True)
        self.save_filter_complex_btn.setEnabled(True)

        # self.is_updating = False  # Флаг для отслеживания обновления

        # Сбрасываем фильтры в модели
        self.models['Tp_nir'].setFilter("")
        self.models['Tp_nir'].select()
        self.tableView_2.setModel(self.models['Tp_nir'])

        # Разблокируем комбобокс по коду ГРНТИ и кнопки
        self.unblock_grnti_filter()

    def filter(self):
        """Открытие меню фильтров."""
        self.reset_filter_state()  # Сброс состояния фильтров перед открытием меню
        self.show_menu(self.Tp_nir_add_row_menu, 3)
        self.hide_buttons()
        self.populate_initial_comboboxes()
        self.setup_combobox_signals()
        self.wid.setVisible(True)
        self.grnticode_cmb.setEnabled(True)

        # Подключение сигналов для фильтрации
        self.filter_by_grnticode_btn.clicked.connect(self.filter_by_cod_grnti)
        self.save_filter_cod_btn.clicked.connect(self.save_filter_grnti)
        self.cancel_filter_cod_btn.clicked.connect(self.on_reset_filter_by_grnti_code)
        self.cancel_filter_complex_btn.clicked.connect(self.on_reset_filter)
        self.save_filter_complex_btn.clicked.connect(self.save_filter_complex)
        self.Tp_nir_redact_filters_close_btn.clicked.connect(self.on_Tp_nir_redact_filters_close_btn_clicked)

        # Обновление модели таблицы для отображения всех записей
        self.models['Tp_nir'].setFilter("")  # Убедитесь, что фильтры сброшены
        self.models['Tp_nir'].select()  # Перезагрузите данные модели
        self.tableView_2.setModel(self.models['Tp_nir'])  # Убедитесь, что модель установлена

    def on_reset_filter_by_grnti_code(self):
        self.clear_and_fill_grnticmb()
        # self.models['VUZ_Summary'].setFilter("")
        # self.models['VUZ_Summary'].select()
        self.models['Tp_nir'].setFilter("")
        self.models['Tp_nir'].select()
        self.tableView_2.setModel(self.models['Tp_nir'])
        # self.tableView_2.reset()
        # self.tableView_2.show()

        self.filter_by_grnticode_btn.setEnabled(True)
        self.grnticode_cmb.setEnabled(True)
        self.menu_1.setEnabled(True)

    def on_reset_filter(self):
        """Сброс комплексного фильтра и возврат к начальному состоянию."""
        # Сброс значений комбобоксов
        self.reset_comboboxes()

        # Сброс фильтров в модели
        self.models['VUZ_Summary'].setFilter("")

        self.models['Tp_nir'].setFilter("")
        self.models['Tp_nir'].select()
        #self.tableView_2.setModel(self.models['Tp_nir'])
        self.table_show_2('Tp_nir')

        # self.clear_and_fill_grnticmb()
        self.save_filter_complex_btn.setEnabled(True)
        self.vuz_cmb.setEnabled(True)
        self.region_cmb.setEnabled(True)
        self.city_cmb.setEnabled(True)
        self.obl_cmb.setEnabled(True)
        self.unblock_grnti_filter()

    def reset_comboboxes(self):
        """Сброс значений комбобоксов к начальному состоянию."""
        self.vuz_cmb.clear()
        self.region_cmb.clear()
        self.city_cmb.clear()
        self.obl_cmb.clear()

        # Заполнение комбобоксов начальными значениями
        self.populate_initial_comboboxes()

        # Устанавливаем "Выберите..." как выбранное значение
        self.vuz_cmb.setCurrentIndex(0)
        self.region_cmb.setCurrentIndex(0)
        self.city_cmb.setCurrentIndex(0)
        self.obl_cmb.setCurrentIndex(0)

    def save_filter_grnti(self):
        """Сохранение условий фильтрации по коду ГРНТИ."""
        str_cod = self.grnticode_cmb.currentData()
        if str_cod:
            self.saved_filter_grnti_conditions.append(str_cod)
            print(f"Сохранено условие фильтрации по ГРНТИ: {str_cod}")
            #self.filter_by_grnticode_btn.setEnabled(False)
            # self.action_show_Tp_nir.setVisible(False)

        else:
            self.show_error_message("Выберите код ГРНТИ для сохранения условия фильтрации.")

    def save_filter_complex(self):
        """Сохранение комплексных условий фильтрации."""

        complex_condition = self.collect_complex_filter_conditions()  # Метод для сбора условий
        if complex_condition:
            self.saved_filter_complex_conditions.append(complex_condition)
            print(f"Сохранено комплексное условие фильтрации: {complex_condition}")
            # Отключаем кнопку комплексной фильтрации
            self.save_filter_complex_btn.setEnabled(False)
            self.vuz_cmb.setEnabled(False)
            self.region_cmb.setEnabled(False)
            self.city_cmb.setEnabled(False)
            self.obl_cmb.setEnabled(False)

        else:
            self.show_error_message("Заполните условия для сохранения комплексного фильтра.")

    def apply_saved_filters(self):
        """Применение сохраненных условий фильтрации."""
        if not (self.saved_filter_grnti_conditions or self.saved_filter_complex_conditions):
            self.show_error_message("Нет сохраненных условий фильтрации.")
            return

        if self.is_updating:
            print("apply_saved_filters: уже выполняется другая операция.")
            return

        conn = QSqlDatabase.database()  # Используем подключение к базе данных
        if not conn.isOpen() and not conn.open():
            print("Ошибка: база данных не открыта.")
            return

        self.is_updating = True  # Устанавливаем флаг обновления

        try:


            self.fill_vuz_summary_with_filters(self.saved_filter_grnti_conditions, self.saved_filter_complex_conditions)


            conn.commit()
            print("Применены сохраненные условия фильтрации по ГРНТИ и комплексные условия.")
        except Exception as e:
            self.show_error_message(f"Ошибка при применении фильтров: {e}")
        finally:
            self.is_updating = False  # Сбрасываем флаг обновления
            conn.close()  # Закрываем соединение с базой данны

    def fill_vuz_summary_with_filters(self, grnti_conditions, complex_conditions):
        """Заполнение таблицы VUZ_Summary с учетом сохраненных условий фильтрации."""
        conn = QSqlDatabase.database()  # Используем подключение к базе данных
        if not conn.isOpen() and not conn.open():
            print("Ошибка: база данных не открыта.")
            return

        try:
            # Начинаем транзакцию
            if not conn.transaction():
                print("Ошибка: не удалось начать транзакцию.")
                return

            # Очистка таблицы перед заполнением
            clear_query = QSqlQuery(conn)
            clear_query.exec('DELETE FROM VUZ_Summary')

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
                      {conditions}
                      GROUP BY VUZ."Сокращенное_имя"
                      HAVING 
                          SUM(Tp_nir."Плановое_финансирование") IS NOT NULL 
                          AND SUM(Tp_fv."Фактическое_финансирование") IS NOT NULL 
                          AND COUNT(Tp_nir."Номер") > 0;
                  '''

            # Формируем строку условий фильтрации
            conditions = ''
            if grnti_conditions:
                # Формируем условия для ГРНТИ
                grnti_conditions_str = ' OR '.join(
                    [f'substr(Tp_nir."Коды_ГРНТИ", 1, 2) = "{cod}"' for cod in grnti_conditions])
                conditions += f' WHERE ({grnti_conditions_str})'

            if complex_conditions:
                # Убедитесь, что complex_conditions является строкой
                if isinstance(complex_conditions, list):
                    complex_conditions_str = ' AND '.join(complex_conditions)  # Объединяем список в строку
                else:
                    complex_conditions_str = complex_conditions  # Если это уже строка

                # Заменяем одинарные кавычки на двойные
                complex_conditions_str = complex_conditions_str.replace("'", '"')

                if conditions:
                    conditions += f' AND {complex_conditions_str}'
                else:
                    conditions += f' WHERE {complex_conditions_str}'

            # Удаляем лишний WHERE, если он не нужен
            if conditions.startswith(' WHERE') and ' AND ' in conditions:
                conditions = conditions.replace(' WHERE', '', 1)

            if conditions:
                query = query.format(conditions=conditions)
            else:
                query = query.format(conditions='')

            print("Сформированный SQL-запрос:", query)  # Отладка: выводим сформированный запрос

            # Выполнение запроса
            insert_query = QSqlQuery(conn)
            if not insert_query.exec(query):
                print(f"Ошибка при выполнении запроса: {insert_query.lastError().text()}")
                conn.rollback()  # Откат транзакции в случае ошибки
                return

            # Добавляем итоговую строку
            total_query = '''
                INSERT INTO VUZ_Summary ("Сокращенное_имя", "Сумма_планового_финансирования", "Сумма_количества_НИР", "Сумма_фактического_финансирования")
                SELECT 
                    'ИТОГО',
                    SUM("Сумма_планового_финансирования"),
                    SUM("Сумма_количества_НИР"),
                    SUM("Сумма_фактического_финансирования")
                FROM VUZ_Summary
            '''
            total_insert_query = QSqlQuery(conn)
            if not total_insert_query.exec(total_query):
                print(f"Ошибка при добавлении итоговой строки: {total_insert_query.lastError().text()}")
                conn.rollback()  # Откат транзакции в случае ошибки
                return

            conn.commit()  # Подтверждаем транзакцию
            print("Таблица VUZ_Summary успешно обновлена.")
            self.models['VUZ_Summary'].select()  # Перезагрузите данные модели
            self.table_show_4('VUZ_Summary')  # Убедитесь, что модель установлена
        except Exception as e:
            print(f"Ошибка при заполнении таблицы VUZ_Summary с фильтрами: {e}")
            conn.rollback()  # Откат транзакции в случае ошибки
        finally:
            conn.close()  # Закрываем соединение с базой данных

    def collect_complex_filter_conditions(self):
        """Сбор комплексных условий фильтрации из комбобоксов."""
        conditions = []
        # Пример сбора условий из комбобоксов
        if self.vuz_cmb.currentIndex() != 0:
            conditions.append(f'VUZ."Сокращенное_имя" = "{self.vuz_cmb.currentText()}"')
        if self.region_cmb.currentIndex() != 0:
            conditions.append(f'VUZ."Регион" = "{self.region_cmb.currentText()}"')
        if self.city_cmb.currentIndex() != 0:
            conditions.append(f'VUZ."Город" = "{self.city_cmb.currentText()}"')
        if self.obl_cmb.currentIndex() != 0:
            conditions.append(f'VUZ."Область" = "{self.obl_cmb.currentText()}"')

        return ' AND '.join(conditions) if conditions else None

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
        self.grnticode_cmb.currentIndexChanged.connect(
            self.on_grnti_code_changed)  # Добавляем обработчик для кода ГРНТИ

    def on_grnti_code_changed(self):
        """Обработчик изменения кода ГРНТИ."""
        if self.grnticode_cmb.currentIndex() != 0:  # Если выбрано значение, отличное от "Выберите..."
            # Сбрасываем комплексные фильтры
            self.region_cmb.setCurrentIndex(0)
            self.city_cmb.setCurrentIndex(0)
            self.obl_cmb.setCurrentIndex(0)
            self.vuz_cmb.setCurrentIndex(0)

            # Выводим сообщение о сбросе фильтров

    def on_vuz_changed(self):
        """Обработчик изменения VUZ."""
        if self.vuz_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.vuz_selected:
            self.vuz_selected = True
            self.update_comboboxes()
            self.update_table()
            # Сбрасываем фильтр по коду ГРНТИ
            self.grnticode_cmb.setCurrentIndex(0)

    def on_region_changed(self):
        """Обработчик изменения региона."""
        if self.region_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.region_selected:
            self.region_selected = True
            self.update_comboboxes()
            self.update_table()
            # Сбрасываем фильтр по коду ГРНТИ
            self.grnticode_cmb.setCurrentIndex(0)

    def on_city_changed(self):
        """Обработчик изменения города."""
        if self.city_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.city_selected:
            self.city_selected = True
            self.update_comboboxes()
            self.update_table()
            # Сбрасываем фильтр по коду ГРНТИ
            self.grnticode_cmb.setCurrentIndex(0)

    def on_obl_changed(self):
        """Обработчик изменения области."""
        if self.obl_cmb.currentIndex() == 0:  # Если выбрано "Выберите..."
            return
        if not self.obl_selected:
            self.obl_selected = True
            self.update_comboboxes()
            self.update_table()
            # Сбрасываем фильтр по коду ГРНТИ
            self.block_grnti_filter()
            self.grnticode_cmb.setCurrentIndex(0)

    def block_grnti_filter(self):
        """Блокировка комбобокса по коду ГРНТИ и связанных кнопок."""
        self.grnticode_cmb.setEnabled(False)
        self.filter_by_grnticode_btn.setEnabled(False)
        self.save_filter_cod_btn.setEnabled(False)
        self.cancel_filter_cod_btn.setEnabled(False)

    def unblock_grnti_filter(self):
        """Разблокировка комбобокса по коду ГРНТИ и связанных кнопок."""
        self.grnticode_cmb.setEnabled(True)
        self.filter_by_grnticode_btn.setEnabled(True)
        self.save_filter_cod_btn.setEnabled(True)
        self.cancel_filter_cod_btn.setEnabled(True)


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
