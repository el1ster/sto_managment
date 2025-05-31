from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import QDate
from datetime import date
from logic.statistics import get_employee_breakdown


class EmployeeExpensesTab(QWidget):
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        self.layout = QVBoxLayout()
        self.init_filters()
        self.init_table()
        self.setLayout(self.layout)

        self.load_data()

    def init_filters(self):
        filter_layout = QHBoxLayout()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())

        self.search_btn = QPushButton("Показати")
        self.search_btn.clicked.connect(self.load_data)

        filter_layout.addWidget(QLabel("Період з:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("по:"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(self.search_btn)

        self.layout.addLayout(filter_layout)

    def init_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Працівник", "Ставка", "Бонус", "Податок", "Сума"])
        self.layout.addWidget(self.table)

    def load_data(self):
        start = self.date_from.date().toPyDate()
        end = self.date_to.date().toPyDate()

        data = get_employee_breakdown(start, end)
        self.table.setRowCount(len(data))

        for row_idx, item in enumerate(data):
            bd = item.get("breakdown", {})
            self.table.setItem(row_idx, 0, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{bd.get('base', 0):.2f}"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{bd.get('bonus', 0):.2f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{bd.get('taxes', 0):.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{item.get('total', 0):.2f}"))
