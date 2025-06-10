from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QLineEdit
)

from PyQt6.QtCore import QDate
from datetime import date
from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord
from logic.accounting_utils import get_total_cost_with_tax
from gui.dialogs.operation_card_dialog import OperationCardDialog
from models.employee import Employee
from gui.dialogs.accounting_report_dialog import AccountingReportDialog
from logic.utils import format_amount
from config import ENTERPRISE_START_DATE


class DateTableItem(QTableWidgetItem):
    def __init__(self, display_text: str, date_value: date | None):
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


class AccountingTab(QWidget):

    def __init__(self, current_user, parent=None):
        try:
            super().__init__(parent)
            self.current_user = current_user
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            # Підсумкові написи
            self.summary_label = QLabel("Сума за період: 0.00 грн")
            self.salary_sum_label = QLabel("Сума зарплат: 0.00 грн")
            self.maintenance_sum_label = QLabel("Сума обслуговувань: 0.00 грн")

            # Кнопка
            self.details_btn = QPushButton("Детальніше")
            self.details_btn.clicked.connect(self.show_detailed_report)

            # --- Фільтри ---
            self.init_filters()

            # --- Підсумки ---
            self.layout.addWidget(self.summary_label)
            self.layout.addWidget(self.salary_sum_label)
            self.layout.addWidget(self.maintenance_sum_label)

            # --- Центрована велика кнопка ---
            btn_layout = QHBoxLayout()
            self.details_btn = QPushButton("Детальніше")
            self.details_btn.setMinimumWidth(200)
            font = self.details_btn.font()
            font.setPointSize(11)
            font.setBold(True)
            self.details_btn.setFont(font)
            self.details_btn.clicked.connect(self.show_detailed_report)
            btn_layout.addStretch()
            btn_layout.addWidget(self.details_btn)
            btn_layout.addStretch()
            self.layout.addLayout(btn_layout)

            # --- Пошук ---
            search_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Пошук по категорії, працівнику або коментарю...")
            self.search_input.textChanged.connect(self.apply_filter)
            search_layout.addWidget(QLabel("Пошук:"))
            search_layout.addWidget(self.search_input)
            self.layout.addLayout(search_layout)

            # Повний список рядків для фільтрації
            self.all_rows = []

            # --- Таблиця ---
            self.init_table()
            self.load_accounting_data()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося ініціалізувати вкладку обліку: {e}")

    def init_filters(self):
        try:
            filter_layout = QHBoxLayout()

            self.date_from = QDateEdit()
            self.date_from.setCalendarPopup(True)
            self.date_from.setDate(
                QDate(ENTERPRISE_START_DATE.year, ENTERPRISE_START_DATE.month, ENTERPRISE_START_DATE.day))

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

            self.table.setSortingEnabled(True)

            self.layout.addWidget(self.table)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити таблицю: {e}")

    def load_accounting_data(self):
        try:
            self.table.setRowCount(0)
            start = self.date_from.date().toPyDate()
            end = self.date_to.date().toPyDate()
            filter_type = self.category_filter.currentData()

            rows = self.fetch_accounting_data(start, end, filter_type)  # 🟢 Спочатку отримуємо дані
            total_salary = sum(r[2] for r in rows if r[1] == "Зарплата")
            total_maintenance = sum(r[2] for r in rows if r[1] == "Обслуговування")
            total_sum = total_salary + total_maintenance

            self.summary_label.setText(f"Сума за період: {format_amount(total_sum)}")
            self.salary_sum_label.setText(f"Сума зарплат: {format_amount(total_salary)}")
            self.maintenance_sum_label.setText(f"Сума обслуговувань: {format_amount(total_maintenance)}")

            self.details_btn.setEnabled(bool(rows))

            self.populate_table(rows)
            self.apply_filter()  # застосувати поточний фільтр одразу

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

            self.all_rows = sorted(rows, key=lambda r: r[0], reverse=True)
            return self.all_rows

        except Exception as e:
            print(f"[CRITICAL] Отримання даних не вдалося: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося отримати дані: {e}")
            return []

    def populate_table(self, rows: list[tuple]):
        try:
            self.table.setRowCount(len(rows))
            for idx, (dt, cat, amount, name, note) in enumerate(rows):
                self.table.setItem(idx, 0, DateTableItem(dt.strftime("%Y-%m-%d"), dt))
                self.table.setItem(idx, 1, QTableWidgetItem(cat))
                self.table.setItem(idx, 2, AmountTableItem(f"{amount:.2f} грн", amount))
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

    def show_detailed_report(self):
        """
        Відкриває діалогове вікно з детальним фінансовим звітом.
        """
        start = self.date_from.date().toPyDate()
        end = self.date_to.date().toPyDate()
        filter_type = self.category_filter.currentData()

        dialog = AccountingReportDialog(start, end, filter_type, self)
        dialog.exec()

    def apply_filter(self):
        """
        Фільтрує таблицю за введеним текстом.
        """
        try:
            text = self.search_input.text().strip().lower()
            if not text:
                self.populate_table(self.all_rows)
                return

            filtered = []
            for row in self.all_rows:
                _, category, _, name, comment = row
                if (text in category.lower() or
                        text in name.lower() or
                        text in (comment or "").lower()):
                    filtered.append(row)

            self.populate_table(filtered)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося застосувати фільтр: {e}")
