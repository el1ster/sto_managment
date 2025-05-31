from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import QDate
from datetime import date
from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord
from models.employee import Employee


class AccountingTab(QWidget):
    """
    Вкладка бухгалтерського обліку: виводить зарплати та обслуговування як витрати.

    Джерела:
        - salary_records (зарплати працівників)
        - maintenance_records (ремонт транспорту)
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        self.layout = QVBoxLayout()
        self.init_filters()
        self.init_table()
        self.setLayout(self.layout)

        self.load_accounting_data()

    def init_filters(self):
        filter_layout = QHBoxLayout()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))

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

    def init_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Дата", "Категорія", "Сума", "Працівник", "Коментар"])
        self.layout.addWidget(self.table)

    def load_accounting_data(self):
        self.table.setRowCount(0)
        start = self.date_from.date().toPyDate()
        end = self.date_to.date().toPyDate()
        filter_type = self.category_filter.currentData()

        rows = []

        if filter_type in [None, "salary"]:
            for rec in SalaryRecord.select().where(SalaryRecord.salary_month.between(start, end)):
                full_name = rec.employee.full_name if rec.employee else "—"
                total = rec.total_payout or 0
                comment = rec.comment or ""
                rows.append((rec.salary_month, "Зарплата", total, full_name, comment))

        if filter_type in [None, "maintenance"]:
            for rec in MaintenanceRecord.select().where(MaintenanceRecord.service_date.between(start, end)):
                full_name = rec.employee.full_name if rec.employee else "—"
                cost = rec.material_cost or 0
                desc = rec.service_desc or ""
                rows.append((rec.service_date, "Обслуговування", cost, full_name, desc))

        self.table.setRowCount(len(rows))
        for idx, (dt, cat, amount, name, note) in enumerate(sorted(rows, key=lambda r: r[0], reverse=True)):
            self.table.setItem(idx, 0, QTableWidgetItem(dt.strftime("%Y-%m-%d")))
            self.table.setItem(idx, 1, QTableWidgetItem(cat))
            self.table.setItem(idx, 2, QTableWidgetItem(f"{amount:.2f} грн"))
            self.table.setItem(idx, 3, QTableWidgetItem(name))
            self.table.setItem(idx, 4, QTableWidgetItem(note))
