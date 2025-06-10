from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from models.maintenance_record import MaintenanceRecord
from logic.accounting_utils import get_total_cost_with_tax
from datetime import date
from collections import defaultdict


class MaintenanceSummaryDialog(QDialog):
    """
    Діалог деталізованого звіту обслуговувань з податками по місяцях.

    Args:
        start (date): Початкова дата періоду.
        end (date): Кінцева дата періоду.
        parent: Батьківський віджет (необов'язково).
    """

    def __init__(self, start: date, end: date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Місячний звіт по обслуговуваннях")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        try:
            records = list(MaintenanceRecord.select().where(
                (MaintenanceRecord.service_date >= start) &
                (MaintenanceRecord.service_date <= end)
            ))

            monthly_totals = defaultdict(float)
            for r in records:
                month_key = r.service_date.strftime("%Y-%m")
                monthly_totals[month_key] += get_total_cost_with_tax(r)

            sorted_months = sorted(monthly_totals.keys())

            table = QTableWidget(len(sorted_months), 2)
            table.setHorizontalHeaderLabels(["Місяць", "Сума (з податками)"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            for row, month in enumerate(sorted_months):
                total = monthly_totals[month]
                table.setItem(row, 0, QTableWidgetItem(month))
                table.setItem(row, 1, QTableWidgetItem(f"{total:,.2f} грн".replace(",", " ")))

            grand_total = sum(monthly_totals.values())
            layout.addWidget(QLabel(f"Загальна сума за період: {grand_total:,.2f} грн".replace(",", " ")))
            layout.addWidget(table)

        except Exception as e:
            layout.addWidget(QLabel(f"Помилка при завантаженні даних: {e}"))
