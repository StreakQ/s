import os
import sqlite3
import csv
import re
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QAbstractItemView,
                             QTableWidget,QInputDialog, QTableWidgetItem, QMenu, QMessageBox)

from PyQt6.QtSql import *
from PyQt6 import QtWidgets, QtCore, uic
from db import *



Form, Window = uic.loadUiType('main_form.ui')
db_name = 'databases//database.db'


def input_cod_grnti(table):
    current_item = table.currentItem()
    menu = QMenu()
    clear_action = menu.addAction("Очистить ячейку")
    add_new_code_action = menu.addAction("Добавить новый код ГРНТИ")
    action = menu.exec(table.mapToGlobal(table.visualItemRect(current_item).center()))

    if action == clear_action:
        table.setItem(current_item.row(), current_item.column(), QTableWidgetItem(""))
    elif action == add_new_code_action:
        while True:
            cod, ok = QInputDialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ из шести цифр '
                                                                     'без разделителей и пробелов')
            if not ok or cod is None or cod.isalpha():
                show_error_message("Неправильное значение. Пожалуйста, введите численные значения.")
                continue
            if len(cod) != 6:
                show_error_message("Неправильное значение. Пожалуйста, введите шесть цифр без разделителей и пробелов.")
                continue
            cod = add_delimiters_to_grnti_code(cod)
            result = str(current_item.text()) + str(cod)
            table.setItem(current_item.row(), current_item.column(), QTableWidgetItem(result.strip()))
            break

def add_delimiters_to_grnti_code(string):
    return "{}.{}.{}".format(string[:2], string[2:4], string[4:])

def show_error_message(message):
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.exec()

def filter_by_cod_grnti():
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        while True:
            str_cod, ok = QInputDialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ или его часть без разделителей и пробелов')
            if not ok or str_cod is None or str_cod.isalpha():
                QMessageBox.warning(None, "Ошибка", "Неправильное значение. Пожалуйста, введите численные значения.")
                return
            else:
                break

        str_cod = add_delimiters_to_grnti_code(str_cod)
        model = QSqlQueryModel()
        query = "SELECT * FROM Tp_nir WHERE `Коды_ГРНТИ` LIKE '%" + str_cod + "%'"
        model.setQuery(query)
        form.tableView.setModel(model)
        form.tableView.show()
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Ошибка", "Ошибка при фильтрации: {}".format(e))
    finally:
        if conn:
            conn.close()

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


#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()
#form.action_.triggered.connect()


window.show()
app.exec()