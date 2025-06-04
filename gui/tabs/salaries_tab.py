from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QAbstractItemView, QHeaderView, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate, Qt
from models.salary_record import SalaryRecord
from models.employee import Employee
from gui.dialogs.add_salary_dialog import AddSalaryDialog
from gui.dialogs.edit_salary_dialog import EditSalaryDialog
from gui.dialogs.salary_card_dialog import SalaryCardDialog



class SalariesTab(QWidget):
    """
    Вкладка для управління записами заробітної плати.
    Доступна повна CRUD-обробка.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        layout = QVBoxLayout(self)

        # --- Фільтр по даті ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Період з:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-24))
        self.start_date.setCalendarPopup(True)
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("по:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filter_layout.addWidget(self.end_date)

        self.filter_btn = QPushButton("Показати")
        self.filter_btn.clicked.connect(self.load_salaries)
        filter_layout.addWidget(self.filter_btn)

        layout.addLayout(filter_layout)

        # --- Таблиця ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Місяць", "Працівник", "Базова зп", "Бонус", "Коментар"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.show_salary_card)

        layout.addWidget(self.table)

        # --- Кнопки ---
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Додати")
        self.edit_btn = QPushButton("Редагувати")
        self.delete_btn = QPushButton("Видалити")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.edit_btn.clicked.connect(self.open_edit_dialog)

        self.load_salaries()

    def load_salaries(self):
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            records = SalaryRecord.select().where(
                (SalaryRecord.salary_month >= start) &
                (SalaryRecord.salary_month <= end)
            )
            self.table.setRowCount(len(records))
            for row, r in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(r.salary_month.strftime("%Y-%m")))
                self.table.setItem(row, 1, QTableWidgetItem(r.employee.full_name))
                self.table.setItem(row, 2, QTableWidgetItem(f"{r.base_salary:.2f} грн"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{r.bonus:.2f} грн"))
                self.table.setItem(row, 4, QTableWidgetItem(r.comment or "-"))
        except Exception as e:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Помилка"])
            self.table.setItem(0, 0, QTableWidgetItem(str(e)))

    def open_add_dialog(self):
        dlg = AddSalaryDialog(self)
        if dlg.exec():
            self.load_salaries()

    def get_selected_salary(self):
        row = self.table.currentRow()
        if row == -1:
            return None
        salary_month = self.table.item(row, 0).text()
        emp_name = self.table.item(row, 1).text()

        # Знаходимо відповідний запис
        for s in SalaryRecord.select():
            if s.salary_month.strftime('%Y-%m') == salary_month and s.employee.full_name == emp_name:
                return s
        return None

    def open_edit_dialog(self):
        print("[open_edit_dialog] Спроба редагування")
        try:
            record = self.get_selected_salary()
            if not record:
                print("[open_edit_dialog] Нічого не обрано")
                QMessageBox.warning(self, "Помилка", "Оберіть запис для редагування.")
                return

            try:
                dlg = EditSalaryDialog(record, self)
                if dlg.exec():
                    print(f"[open_edit_dialog] Змінено запис ID={record.id}")
                    self.load_salaries()
            except Exception as inner_e:
                print(f"[open_edit_dialog][ERROR][Dialog] {inner_e}")
                QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити діалог редагування: {inner_e}")

        except Exception as e:
            print(f"[open_edit_dialog][ERROR] {e}")
            QMessageBox.critical(self, "Помилка", f"Помилка при редагуванні запису: {e}")

    def delete_selected(self):
        salary = self.get_selected_salary()
        if not salary:
            QMessageBox.warning(self, "Помилка", "Оберіть запис для видалення.")
            return
        confirm = QMessageBox.question(
            self, "Підтвердження",
            f"Видалити запис за {salary.salary_month.strftime('%Y-%m')} для {salary.employee.full_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            salary.delete_instance()
            self.load_salaries()

    def show_salary_card(self, index):
        print("[show_salary_card] Дабл-клік по таблиці")
        try:
            try:
                record = self.get_selected_salary()
                if not record:
                    print("[show_salary_card] Запис не вибрано")
                    return
            except Exception as get_err:
                print(f"[show_salary_card][ERROR][get_selected_salary] {get_err}")
                QMessageBox.critical(self, "Помилка", f"Помилка при отриманні запису: {get_err}")
                return

            try:
                dlg = SalaryCardDialog(record, self)
                dlg.exec()
                print(f"[show_salary_card] Картка показана: {record.employee.full_name}, {record.salary_month}")
            except Exception as dialog_err:
                print(f"[show_salary_card][ERROR][Dialog] {dialog_err}")
                QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити картку зарплати: {dialog_err}")

        except Exception as e:
            print(f"[show_salary_card][ERROR][Unexpected] {e}")
            QMessageBox.critical(self, "Помилка", f"Невідома помилка: {e}")

