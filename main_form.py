from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QAbstractItemView,
                             QTableWidget, QInputDialog, QTableWidgetItem, QMenu, QMessageBox, QComboBox,
                             QStackedWidget, QToolBar, QHeaderView)
from PyQt6.QtSql import QSqlQueryModel, QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from db import *

class VUZ:
    def __init__(self, code, name, full_name, short_name, region, city, status, area_code, area, type, prof):
        self.code = code
        self.name = name
        self.full_name = full_name
        self.short_name = short_name
        self.region = region
        self.city = city
        self.status = status
        self.area_code = area_code
        self.area = area
        self.type = type
        self.prof = prof

class Tp_nir:
    def __init__(self, code, number, character, short_name, leader, grnti_codes, nir, position, planned_financing):
        self.code = code
        self.number = number
        self.character = character
        self.short_name = short_name
        self.leader = leader
        self.grnti_codes = grnti_codes
        self.nir = nir
        self.position = position
        self.planned_financing = planned_financing

class Grntirub:
    def __init__(self, code, name):
        self.code = code
        self.name = name

class Tp_fv:
    def __init__(self, code, short_name, planned_financing, actual_financing, nir_count):
        self.code = code
        self.short_name = short_name
        self.planned_financing = planned_financing
        self.actual_financing = actual_financing
        self.nir_count = nir_count

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Main Window')

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tableView = QTableWidget()
        self.layout.addWidget(self.tableView)

        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.Tp_nir_redact_widget = QWidget()
        self.layout.addWidget(self.Tp_nir_redact_widget)

        self.add_widget_open_pushButton = QPushButton('Add Widget')
        self.layout.addWidget(self.add_widget_open_pushButton)

        self.redact_widget_open_pushButton = QPushButton('Redact Widget')
        self.layout.addWidget(self.redact_widget_open_pushButton)

        self.add_widget_open_pushButton.clicked.connect(self.add_widget)
        self.redact_widget_open_pushButton.clicked.connect(self.redact_widget)

        self.stackedWidget = QStackedWidget()
        self.layout.addWidget(self.stackedWidget)

        self.page = QWidget()
        self.stackedWidget.addWidget(self.page)

        self.page_add_widget = QWidget()
        self.stackedWidget.addWidget(self.page_add_widget)

        self.page_redact_widget = QWidget()
        self.stackedWidget.addWidget(self.page_redact_widget)

        self.add_confirm_widget = QWidget()
        self.layout.addWidget(self.add_confirm_widget)

        self.redact_confirm_widget = QWidget()
        self.layout.addWidget(self.redact_confirm_widget)

        self.add_confirm_widget.setVisible(False)
        self.redact_confirm_widget.setVisible(False)

        self.Tp_nir_add_grntiNature_comboBox = QComboBox()
        self.Tp_nir_add_grntiNature_comboBox.addItems(["П", "Р", "Ф"])

        self.Tp_nir_add_VUZcode_name_comboBox = QComboBox()
        self.Tp_nir_add_VUZcode_name_comboBox.addItems([str(i) + ' ' + var for var, i in zip(column(), codes())])

        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.toolbar = QToolBar()
        self.layout.addWidget(self.toolbar)

        self.action_show_VUZ = QAction('VUZ')
        self.action_show_Tp_nir = QAction('Tp_nir')
        self.action_show_grntirub = QAction('Grntirub')
        self.action_show_Tp_fv = QAction('Tp_fv')

        self.toolbar.addAction(self.action_show_VUZ)
        self.toolbar.addAction(self.action_show_Tp_nir)
        self.toolbar.addAction(self.action_show_grntirub)
        self.toolbar.addAction(self.action_show_Tp_fv)

        self.action_show_VUZ.triggered.connect(self.table_show_VUZ)
        self.action_show_Tp_nir.triggered.connect(self.table_show_Tp_nir)
        self.action_show_grntirub.triggered.connect (self.table_show_grntirub)
        self.action_show_Tp_fv.triggered.connect(self.table_show_Tp_fv)

    def add_widget(self):
        self.stackedWidget.setCurrentIndex(1)

    def redact_widget(self):
        self.stackedWidget.setCurrentIndex(2)

    def table_show_VUZ(self):
        self.tableView.clearContents()
        self.tableView.setRowCount(0)
        query = QSqlQueryModel()
        query.setQuery("SELECT * FROM VUZ")
        self.tableView.setModel(query)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def table_show_Tp_nir(self):
        self.tableView.clearContents()
        self.tableView.setRowCount(0)
        query = QSqlQueryModel()
        query.setQuery("SELECT * FROM Tp_nir")
        self.tableView.setModel(query)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def table_show_grntirub(self):
        self.tableView.clearContents()
        self.tableView.setRowCount(0)
        query = QSqlQueryModel()
        query.setQuery("SELECT * FROM Grntirub")
        self.tableView.setModel(query)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def table_show_Tp_fv(self):
        self.tableView.clearContents()
        self.tableView.setRowCount(0)
        query = QSqlQueryModel()
        query.setQuery("SELECT * FROM Tp_fv")
        self.tableView.setModel(query)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)