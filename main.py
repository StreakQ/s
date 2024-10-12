import os
import sqlite3
import csv
import re
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QAbstractItemView,
                             QTableWidget,QInputDialog, QTableWidgetItem, QMenu, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtSql import *
from PyQt6 import QtWidgets, QtCore, uic
from db import *



Form, Window = uic.loadUiType('main_form.ui')
db_name = 'databases//database.db'


def input_cod_grnti(table):
    print("Функция input_cod_grnti вызвана")
    selection_model = table.selectionModel()
    selected_indexes = selection_model.selectedIndexes()
    if not selected_indexes:
        print("Ошибка: не выбран текущий элемент")
        return

    current_index = selected_indexes[0]
    record = table.model().record(current_index.row())
    current_value = record.value(current_index.column())

    print("Текущий элемент:", current_value)

    menu = QMenu()
    clear_action = menu.addAction("Очистить ячейку")
    add_new_code_action = menu.addAction("Добавить новый код ГРНТИ")
    action = menu.exec(table.mapToGlobal(table.visualRect(current_index).center()))

    if action == clear_action:
        print("Действие очистки выбрано")
        try:
            table.model().setData(current_index, "", Qt.ItemDataRole.EditRole)
        except Exception as e:
            print(f"Ошибка очистки элемента: {e}")
    elif action == add_new_code_action:
        print("Действие добавления нового кода ГРНТИ выбрано")
        while True:
            cod, ok = QInputDialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ из шести цифр '
                                                                     'без разделителей и пробелов')
            if not ok:
                print("Диалог ввода отменен")
                break
            if cod is None or cod.isalpha():
                print("Неверный ввод: пожалуйста, введите 6-значный код")
                continue
            if len(cod) != 6:
                print("Неверный ввод: код должен быть 6 цифр длинной")
                continue
            cod = add_delimiters_to_grnti_code(cod)
            result = str(current_value) + str(cod)
            try:
                table.model().setData(current_index, result.strip(), Qt.ItemDataRole.EditRole)
            except Exception as e:
                print(f"Ошибка установки элемента: {e}")
            break


def add_delimiters_to_grnti_code(string):
    if len(string) == 2:
        return "{}.".format(string)
    elif len(string) == 4:
        return "{}.{}".format(string[:2], string[2:])
    else:
        return "{}.{}.{}".format(string[:2], string[2:4], string[4:])

def show_error_message(message):
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.exec()

def filter_by_cod_grnti():
    try:
        while True:
            str_cod, ok = QInputDialog.getText(None, "Введите значение",
                                               'Введите весь код ГРНТИ или его часть без разделителей и пробелов')
            if not ok:
                return
            if str_cod is None or str_cod.isalpha():
                QMessageBox.warning(None, "Ошибка", "Неправильное значение. Пожалуйста, введите численные значения.")
                return
            else:
                break
        str_cod = str_cod.strip()
        str_cod = add_delimiters_to_grnti_code(str_cod)
        query = f' "Коды_ГРНТИ" LIKE "{str_cod}%" OR "Коды_ГРНТИ" LIKE ";{str_cod}%" '
        Tp_nir.setFilter(query)
        Tp_nir.select()
        form.tableView.setModel(Tp_nir)
        form.tableView.reset()
        form.tableView.show()
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", "Ошибка при фильтрации: {}".format(e))

name_list=column()
code_list=codes()
#prepare_tables()
#[str(i) + ' ' + var for var, i in zip(name_list, range(1,100))]

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

def connect_db(db_name_name):
    db_name = QSqlDatabase.addDatabase('QSQLITE')
    db_name.setDatabaseName(db_name_name)
    if not db_name.open():
        print('не удалось подключиться к базе')
        return False
    return db_name

if not connect_db(db_name):
    sys.exit(-1)
else:
    print('Connection OK')

VUZ = QSqlTableModel()
VUZ.setTable('VUZ')
VUZ.select()

Tp_nir = QSqlTableModel()
Tp_nir.setTable('Tp_nir')
Tp_nir.select()

grntirub = QSqlTableModel()
grntirub.setTable('grntirub')
grntirub.select()

Tp_fv = QSqlTableModel()
Tp_fv.setTable('Tp_fv')
Tp_fv.select()

form.tableView.setSortingEnabled(True)
form.tableView.horizontalHeader().setStretchLastSection(True)
form.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
#form.widget.
form.Tp_nir_redact_widget.setVisible(False)

form.add_confirm_widget.setVisible(False)
form.redact_confirm_widget.setVisible(False)
form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
form.stackedWidget.setCurrentWidget(form.page)

def table_show_VUZ():
    form.tableView.setModel(VUZ)
    form.Tp_nir_redact_widget.setVisible(False)

def table_show_Tp_nir():
    form.tableView.setModel(Tp_nir)
    form.Tp_nir_redact_widget.setVisible(True)

def table_show_grntirub():
    form.tableView.setModel(grntirub)
    form.Tp_nir_redact_widget.setVisible(False)

def table_show_Tp_fv():
    form.tableView.setModel(Tp_fv)
    form.Tp_nir_redact_widget.setVisible(False)

def selectRows():
    form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

def selectColums():
    form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectColumns)

def selectItems():
    form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)

def add_widget():
    form.stackedWidget.setCurrentWidget(form.page_add_widget)

def redact_widget():
    form.stackedWidget.setCurrentWidget(form.page_redact_widget)

def close_add_widget():
    form.stackedWidget.setCurrentWidget(form.page)

def close_redact_widget():
    form.stackedWidget.setCurrentWidget(form.page)

def save_add_widget():
    form.add_confirm_widget.setVisible(True)

def save_redact_widget():
    form.redact_confirm_widget.setVisible(True)

def close_add_confirm():
    form.add_confirm_widget.setVisible(False)
    form.stackedWidget.setCurrentWidget(form.page)

def close_redact_confirm():
    form.redact_confirm_widget.setVisible(False)
    form.stackedWidget.setCurrentWidget(form.page)



form.action_show_VUZ.triggered.connect(table_show_VUZ)
form.action_show_Tp_nir.triggered.connect(table_show_Tp_nir)
form.action_show_grntirub.triggered.connect(table_show_grntirub)
form.action_show_Tp_fv.triggered.connect(table_show_Tp_fv)
form.Tp_nir_add_grntiNature_comboBox.addItems(["П", "Р", "Ф"])
form.Select_rows_action.triggered.connect(selectRows)
form.Select_columns_action.triggered.connect(selectColums)
form.Select_items_action.triggered.connect(selectItems)
form.add_widget_open_pushButton.clicked.connect(add_widget)
form.redact_widget_open_pushButton.clicked.connect(redact_widget)
form.add_widget_close_pushButton.clicked.connect(close_add_widget)
form.redact_widget_close_pushButton.clicked.connect(close_redact_widget)
form.Tp_nir_add_widget_saveButton.clicked.connect(save_add_widget)
form.redact_widget_saveButton.clicked.connect(save_redact_widget)
form.close_add_confirm_pushButton.clicked.connect(close_add_confirm)
form.close_redact_confirm_pushButton.clicked.connect(close_redact_confirm)
form.Tp_nir_add_VUZcode_name_comboBox.addItems([str(i) + ' ' + var for var, i in zip(name_list, code_list)] )



#form.add_widget_open_pushButton.clicked.connect()
#form.redact_widget_open_pushButton.clicked.connect()
form.widget_del_pushButton.clicked.connect(lambda: delete_string_in_table(form.tableView, form.tableView.model()))
#form.add_widget_close_pushButton.clicked.connect()
form.widget_add_grnti_cod_pushbutton.clicked.connect(lambda: input_cod_grnti(form.tableView))
form.widget_filter_grnti_cod_pushButton.clicked.connect(filter_by_cod_grnti)
form.widget_hard_filter_pushButton.clicked.connect(hard_filter)

#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()


window.show()
app.exec()