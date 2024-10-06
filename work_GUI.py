

def get_selected_cell():
    table = QTableWidget()
    selection = table.selectionModel()
    indexes = selection.selectedIndexes()
    if indexes:
        index = indexes[0]
        row = index.row()
        column = index.column()
        return table, row, column
    else:
        return None, None, None


def input_cod_grnti():
    """ВВод кода ГРНТИ без разделителей в определенную существующую ячейку"""
    table, row, column = get_selected_cell()
    item = table.item(row, column)
    grnti_pattern = r'\d{2}\.\d{2}\.\d{2}'
    if re.search(grnti_pattern, str(item.text())):
        menu = QMenu()
        clear_action = menu.addAction("Очистить ячейку")
        add_new_code_action = menu.addAction("Добавить новый код")
        action = menu.exec_(table.mapToGlobal(table.visualItemRect(item).center()))

        if action == clear_action:
            table.setItem(row, column, QTableWidgetItem(""))
        elif action == add_new_code_action:
            input_dialog = QInputDialog()
            while True:
                cod, ok = input_dialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ без разделителей и пробелов')
                if not ok or cod is None or cod.isalpha():
                    msg_box = QMessageBox()
                    msg_box.setText("Неправильное значение. Пожалуйста, введите численные значения.")
                    msg_box.exec()
                    return None
                else:
                    break

            cod = add_delimiters_in_cod_grnti(cod)
            result = str(item.text()) + str(cod)
            result.strip()
            table.setItem(row, column, QTableWidgetItem(result))
    else:
        input_dialog = QInputDialog()
        while True:
            cod, ok = input_dialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ без разделителей и пробелов')
            if not ok or cod is None or cod.isalpha():
                msg_box = QMessageBox()
                msg_box.setText("Неправильное значение. Пожалуйста, введите численные значения.")
                msg_box.exec()
                return None
            else:
                break
        cod = add_delimiters_in_cod_grnti(cod)
        result = str(item.text()) + str(cod)
        result.strip()
        table.setItem(row, column, QTableWidgetItem(result))

def add_delimiters_in_cod_grnti(string):
    """Добавление точек между каждой парой цифр в вводимый код ГРНТИ"""
    string = string.strip()
    if len(string) > 8:
        string = string[:9]
    for i in range(2, len(string) - 2, 2):
        string[i] = string[i] + '.'
    return string

def filter_by_cod_grnti():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    input_dialog = QInputDialog()
    while True:
        str_cod, ok = input_dialog.getText(None, "Введите значение", 'Введите весь код ГРНТИ или его часть без разделителей и пробелов')
        if not ok or str_cod is None or str_cod.isalpha():
            msg_box = QMessageBox()
            msg_box.setText("Неправильное значение. Пожалуйста, введите численные значения.")
            msg_box.exec()
            return None
        else:
            break

    str_cod = add_delimiters_in_cod_grnti(str_cod)
    c.execute('''SELECT *   
                            FROM Tp_nir
                            WHERE "Коды_ГРНТИ" LIKE ?''', ('%' + str_cod + '%',))
    rows = c.fetchall()
    headers = [description[0] for description in c.description]
    model = QSqlQueryModel()
    model.setQuery("SELECT * FROM Tp_nir WHERE `Коды_ГРНТИ` LIKE '%" + str_cod + "%'")
    form.tableView.setModel(model)
    form.tableView.show()
    conn.commit()
    conn.close()