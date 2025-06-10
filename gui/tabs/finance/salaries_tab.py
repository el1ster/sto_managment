from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QAbstractItemView, QHeaderView, QDateEdit, QMessageBox, QLineEdit
)

from gui.dialogs.add_salary_dialog import AddSalaryDialog
from gui.dialogs.edit_salary_dialog import EditSalaryDialog
from gui.dialogs.salary_card_dialog import SalaryCardDialog
from models.salary_record import SalaryRecord
from logic.accounting_utils import get_total_cost_with_tax
from datetime import date

class DateTableItem(QTableWidgetItem):
    def __init__(self, display_text: str, date_value: date):
        super().__init__(display_text)
        self.date_value = date_value or date.min

    def __lt__(self, other):
        if isinstance(other, DateTableItem):
            return self.date_value < other.date_value
        return super().__lt__(other)


class AmountTableItem(QTableWidgetItem):
    def __init__(self, display_text: str, amount: float):
        super().__init__(display_text)
        self.amount = amount

    def __lt__(self, other):
        if isinstance(other, AmountTableItem):
            return self.amount < other.amount
        return super().__lt__(other)


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

        # --- Сума зарплат + кнопка ---
        self.total_label = QLabel("Сума зарплат: 0.00 грн")
        self.details_btn = QPushButton("Детальніше")
        self.details_btn.setMinimumWidth(150)
        self.details_btn.clicked.connect(self.show_summary_dialog)

        total_layout = QHBoxLayout()
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.details_btn)
        layout.addLayout(total_layout)

        # --- Пошук ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по ПІБ, місяцю або коментарю...")
        self.search_input.textChanged.connect(self.apply_filter)
        search_layout.addWidget(QLabel("Пошук:"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Повний список записів
        self.all_records = []

        # --- Таблиця ---
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Місяць", "Працівник", "Базова зп", "Бонус", "Без податків", "З податками", "Коментар"
        ])
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

    from logic.accounting_utils import get_total_cost_with_tax

    ...

    def load_salaries(self):
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()

            self.all_records = list(
                SalaryRecord.select().where(
                    (SalaryRecord.salary_month >= start) &
                    (SalaryRecord.salary_month <= end)
                )
            )

            # Загальна сума з податками
            total = sum(get_total_cost_with_tax(r) for r in self.all_records)
            self.total_label.setText(f"Сума зарплат (з податками): {total:,.2f} грн".replace(",", " "))
            self.details_btn.setEnabled(bool(self.all_records))

            # Заповнюємо таблицю з урахуванням фільтра
            self.apply_filter()

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

    def show_summary_dialog(self):
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()

            from gui.dialogs.salary_summary_dialog import SalarySummaryDialog
            dlg = SalarySummaryDialog(start, end, self)
            dlg.exec()

        except Exception as e:
            print(f"[show_summary_dialog][ERROR] {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити діалог деталізації: {e}")

    def apply_filter(self):
        try:
            text = self.search_input.text().strip().lower()
            filtered = []

            for r in self.all_records:
                month = r.salary_month.strftime("%Y-%m").lower()
                name = r.employee.full_name.lower()
                comment = (r.comment or "").lower()

                if text in month or text in name or text in comment:
                    filtered.append(r)

            self.table.setRowCount(len(filtered))
            for row, r in enumerate(filtered):
                no_tax_sum = float(r.base_salary + r.bonus)
                with_tax_sum = get_total_cost_with_tax(r)
                month_date = r.salary_month

                self.table.setSortingEnabled(False)
                self.table.setItem(row, 0, DateTableItem(month_date.strftime("%Y-%m"), month_date))
                self.table.setItem(row, 1, QTableWidgetItem(r.employee.full_name))
                self.table.setItem(row, 2, AmountTableItem(f"{r.base_salary:.2f} грн", float(r.base_salary)))
                self.table.setItem(row, 3, AmountTableItem(f"{r.bonus:.2f} грн", float(r.bonus)))
                self.table.setItem(row, 4, AmountTableItem(f"{no_tax_sum:,.2f} грн".replace(",", " "), no_tax_sum))
                self.table.setItem(row, 5, AmountTableItem(f"{with_tax_sum:,.2f} грн".replace(",", " "), with_tax_sum))
                self.table.setItem(row, 6, QTableWidgetItem(r.comment or "-"))
                self.table.setSortingEnabled(True)


        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося застосувати фільтр: {e}")

