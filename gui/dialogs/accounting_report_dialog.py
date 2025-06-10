from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from logic.accounting_utils import get_total_cost_with_tax
from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord
from models.employee import Employee
from datetime import date
from collections import defaultdict


class AccountingReportDialog(QDialog):
    """
    Діалогове вікно для перегляду сум витрат по місяцях (таблично).
    """

    def __init__(self, start: date, end: date, category_filter=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Звіт: суми по місяцях")
        self.setMinimumSize(650, 500)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Період: {start.strftime('%Y-%m-%d')} — {end.strftime('%Y-%m-%d')}"))

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Місяць", "Обслуговування", "Зарплата", "Сума"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        self.populate_monthly_table(start, end, category_filter)

    def populate_monthly_table(self, start: date, end: date, category_filter=None):
        salary_by_month = defaultdict(float)
        maintenance_by_month = defaultdict(float)

        if category_filter in [None, "salary"]:
            for rec in SalaryRecord.select().where(SalaryRecord.salary_month.between(start, end)):
                try:
                    key = rec.salary_month.replace(day=1)
                    salary_by_month[key] += get_total_cost_with_tax(rec)
                except Exception as e:
                    print(f"[ERROR] SalaryRecord: {e}")

        if category_filter in [None, "maintenance"]:
            for rec in MaintenanceRecord.select().where(MaintenanceRecord.service_date.between(start, end)):
                try:
                    key = rec.service_date.replace(day=1)
                    maintenance_by_month[key] += get_total_cost_with_tax(rec)
                except Exception as e:
                    print(f"[ERROR] MaintenanceRecord: {e}")

        # Об'єднати всі ключі
        all_months = sorted(set(salary_by_month.keys()) | set(maintenance_by_month.keys()))
        self.table.setRowCount(len(all_months))

        for row, month in enumerate(all_months):
            month_str = month.strftime("%B %Y").capitalize()
            salary = salary_by_month.get(month, 0.0)
            maintenance = maintenance_by_month.get(month, 0.0)
            total = salary + maintenance

            self.table.setItem(row, 0, QTableWidgetItem(month_str))
            self.table.setItem(row, 1, QTableWidgetItem(f"{maintenance:.2f} грн"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{salary:.2f} грн"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{total:.2f} грн"))
