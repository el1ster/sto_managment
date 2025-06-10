from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from models.salary_record import SalaryRecord
from datetime import date
from collections import defaultdict


class SalarySummaryDialog(QDialog):
    def __init__(self, start: date, end: date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Зарплати по місяцях")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Період: {start} — {end}"))

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Місяць", "Сума"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.load_data(start, end)

    def load_data(self, start: date, end: date):
        data = defaultdict(float)

        for r in SalaryRecord.select().where((SalaryRecord.salary_month >= start) & (SalaryRecord.salary_month <= end)):
            key = r.salary_month.replace(day=1)
            data[key] += float(r.base_salary) + float(r.bonus)


        rows = sorted(data.items())
        self.table.setRowCount(len(rows))
        for i, (month, total) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(month.strftime("%B %Y").capitalize()))
            self.table.setItem(i, 1, QTableWidgetItem(f"{total:,.2f} грн".replace(",", " ")))
