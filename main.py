import os
import sqlite3
import csv

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QAbstractItemView
from PyQt6.QtSql import *
from PyQt6 import QtWidgets, QtCore, uic
from db import prepare_tables, connect_db
from work_GUI import get_selected_cell, input_cod_grnti,add_delimiters_in_cod_grnti, filter_by_cod_grnti


Form, Window = uic.loadUiType('main_form.ui')
db_name = 'databases//database.db'


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
    while (1):
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