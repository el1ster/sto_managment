from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)

from PyQt6.QtCore import QDate
from datetime import date
from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord
from logic.accounting_utils import get_total_cost_with_tax
from gui.dialogs.operation_card_dialog import OperationCardDialog
from models.employee import Employee


class AccountingTab(QWidget):
    def __init__(self, current_user, parent=None):
        try:
            super().__init__(parent)
            self.current_user = current_user
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            self.init_filters()
            self.init_table()
            self.load_accounting_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося ініціалізувати вкладку обліку: {e}")

    def init_filters(self):
        try:
            filter_layout = QHBoxLayout()

            self.date_from = QDateEdit()
            self.date_from.setCalendarPopup(True)
            self.date_from.setDate(QDate.currentDate().addMonths(-24))

            self.date_to = QDateEdit()
            self.date_to.setCalendarPopup(True)
            self.date_to.setDate(QDate.currentDate())

            self.category_filter = QComboBox()
            self.category_filter.addItem("Усі категорії", None)
            self.category_filter.addItem("Зарплата", "salary")
            self.category_filter.addItem("Обслуговування", "maintenance")

            self.search_btn = QPushButton("Показати")
            self.search_btn.clicked.connect(self.load_accounting_data)

            filter_layout.addWidget(QLabel("Період з:"))
            filter_layout.addWidget(self.date_from)
            filter_layout.addWidget(QLabel("по:"))
            filter_layout.addWidget(self.date_to)
            filter_layout.addWidget(QLabel("Категорія:"))
            filter_layout.addWidget(self.category_filter)
            filter_layout.addWidget(self.search_btn)

            self.layout.addLayout(filter_layout)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити фільтри: {e}")

    def init_table(self):
        try:
            self.table = QTableWidget()
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["Дата", "Категорія", "Сума", "Працівник", "Коментар"])
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.table.cellDoubleClicked.connect(self.open_operation_card)

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

            self.layout.addWidget(self.table)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити таблицю: {e}")

    def load_accounting_data(self):
        try:
            self.table.setRowCount(0)
            start = self.date_from.date().toPyDate()
            end = self.date_to.date().toPyDate()
            filter_type = self.category_filter.currentData()

            rows = self.fetch_accounting_data(start, end, filter_type)
            self.populate_table(rows)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити дані: {e}")

    def fetch_accounting_data(self, start: date, end: date, filter_type=None) -> list[tuple]:
        try:
            rows = []

            if filter_type in [None, "salary"]:
                for rec in SalaryRecord.select().where(SalaryRecord.salary_month.between(start, end)):
                    try:
                        full_name = rec.employee.full_name if rec.employee else "—"
                        comment = rec.comment or ""
                        total = get_total_cost_with_tax(rec)
                        rows.append((rec.salary_month, "Зарплата", total, full_name, comment))
                    except Exception as e:
                        print(f"[ERROR] SalaryRecord помилка: {e}")
                        continue

            if filter_type in [None, "maintenance"]:
                 for rec in MaintenanceRecord.select().where(MaintenanceRecord.service_date.between(start, end)):
                    try:
                        full_name = rec.employee.full_name if rec.employee else "—"
                        desc = rec.service_desc or ""
                        total = get_total_cost_with_tax(rec)
                        rows.append((rec.service_date, "Обслуговування", total, full_name, desc))
                    except Exception as e:
                        print(f"[ERROR] MaintenanceRecord помилка: {e}")
                        continue

            return sorted(rows, key=lambda r: r[0], reverse=True)
        except Exception as e:
            print(f"[CRITICAL] Отримання даних не вдалося: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося отримати дані: {e}")
            return []

    def populate_table(self, rows: list[tuple]):
        try:
            self.table.setRowCount(len(rows))
            for idx, (dt, cat, amount, name, note) in enumerate(rows):
                self.table.setItem(idx, 0, QTableWidgetItem(dt.strftime("%Y-%m-%d")))
                self.table.setItem(idx, 1, QTableWidgetItem(cat))
                self.table.setItem(idx, 2, QTableWidgetItem(f"{amount:.2f} грн"))
                self.table.setItem(idx, 3, QTableWidgetItem(name))
                self.table.setItem(idx, 4, QTableWidgetItem(note))
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося заповнити таблицю: {e}")

    def open_operation_card(self, row: int, column: int):
        """
        Відкриває діалогову карту для вибраної операції (зарплати чи обслуговування).

        Args:
            row (int): Індекс рядка таблиці.
            column (int): Індекс колонки таблиці.
        """
        try:
            print(f"[INFO] Спроба відкриття карти операції для рядка {row}, колонки {column}")

            # Зчитування даних із таблиці
            date_str = self.table.item(row, 0).text()
            category = self.table.item(row, 1).text()
            name = self.table.item(row, 3).text()

            print(f"[DEBUG] Зчитано дані з таблиці: дата={date_str}, категорія={category}, працівник={name}")

            rec = None
            dt = date.fromisoformat(date_str)

            if category == "Зарплата":
                print(f"[INFO] Пошук запису зарплати на дату {dt} для працівника {name}")
                rec = SalaryRecord.select().join(Employee).where(
                    SalaryRecord.salary_month == dt,
                    Employee.full_name == name
                ).first()

            elif category == "Обслуговування":
                print(f"[INFO] Пошук запису обслуговування на дату {dt} для працівника {name}")
                rec = MaintenanceRecord.select().join(Employee).where(
                    MaintenanceRecord.service_date == dt,
                    Employee.full_name == name
                ).first()

            else:
                print(f"[WARN] Невідома категорія: {category}")
                return

            if rec:
                print(f"[INFO] Запис знайдено. Відкривається карта операції.")
                dialog = OperationCardDialog(rec, self)
                dialog.exec()
            else:
                print(f"[WARN] Не вдалося знайти відповідний запис.")
                QMessageBox.warning(self, "Не знайдено", "Не вдалося знайти відповідний запис.")

        except Exception as e:
            print(f"[ERROR] Помилка при відкритті карти операції: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити карту операції: {e}")


