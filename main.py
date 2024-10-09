import os
import sqlite3
import csv
import re
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QAbstractItemView,
                             QTableWidget,QInputDialog, QTableWidgetItem, QMenu, QMessageBox)

from PyQt6.QtSql import *
from PyQt6 import QtWidgets, QtCore, uic
from db import prepare_tables, connect_db



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

prepare_tables()


app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)



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
form.add_widget.setVisible(False)
form.VUZ_add_widget.setVisible(False)
form.Tp_nir_add_widget.setVisible(False)
form.grntirub_add_widget.setVisible(False)
form.Tp_fv_add_widget.setVisible(False)
form.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)


def table_show_VUZ():
    form.tableView.setModel(VUZ)
    table_model='VUZ'

def table_show_Tp_nir():
    form.tableView.setModel(Tp_nir)
    table_model = 'Tp_nir'

def table_show_grntirub():
    form.tableView.setModel(grntirub)
    table_model = 'grntirub'

def table_show_Tp_fv():
    form.tableView.setModel(Tp_fv)
    table_model = 'Tp_fv'

def add_widget_switch():
    form.add_widget.setVisible(not form.add_widget.isVisible())

def close_add_widget():
    form.add_widget.setVisible(False)

def add_widget_refresh():
    while True:
        if (form.add_tableChoice_comboBox.currentIndex() ==1):
            form.VUZ_add_widget.setVisible(True)
            form.Tp_nir_add_widget.setVisible(False)
            form.grntirub_add_widget.setVisible(False)
            form.Tp_fv_add_widget.setVisible(False)
        if (form.add_tableChoice_comboBox.currentIndex() ==2):
            form.VUZ_add_widget.setVisible(False)
            form.Tp_nir_add_widget.setVisible(True)
            form.grntirub_add_widget.setVisible(False)
            form.Tp_fv_add_widget.setVisible(False)
        if (form.add_tableChoice_comboBox.currentIndex() ==3):
            form.VUZ_add_widget.setVisible(False)
            form.Tp_nir_add_widget.setVisible(False)
            form.grntirub_add_widget.setVisible(True)
            form.Tp_fv_add_widget.setVisible(False)
        if (form.add_tableChoice_comboBox.currentIndex() ==4):
            form.VUZ_add_widget.setVisible(False)
            form.Tp_nir_add_widget.setVisible(False)
            form.grntirub_add_widget.setVisible(False)
            form.Tp_fv_add_widget.setVisible(True)
        break

form.action_show_VUZ.triggered.connect(table_show_VUZ)
form.action_show_Tp_nir.triggered.connect(table_show_Tp_nir)
form.action_show_grntirub.triggered.connect(table_show_grntirub)
form.action_show_Tp_fv.triggered.connect(table_show_Tp_fv)
form.action_add.triggered.connect(add_widget_switch)
form.add_widget_close_pushButton1.clicked.connect(close_add_widget)
form.add_widget_close_pushButton2.clicked.connect(close_add_widget)
form.add_widget_close_pushButton3.clicked.connect(close_add_widget)
form.add_widget_close_pushButton4.clicked.connect(close_add_widget)
form.Tp_nir_add_grntiNature_comboBox.addItems(["-Выберите характер НИР-", "П", "Р", "Ф"])
form.add_tableChoice_comboBox.addItems(["-Выберите таблицу-","VUZ","Tp_nir","grntirub","Tp_fv"])
form.VUZ_add_VUZtype_comboBox.addItems(["-Выберите тип учебного заведения-"," ","ФУ","ПСР","НИУ"])
form.VUZ_add_profile_comboBox.addItems(["-Выберите профиль ВУЗа-"," ","МП","КЛ","ИТ","ГП"])
form.add_widget_reload_pushButton.clicked.connect(add_widget_refresh)




window.show()
app.exec()