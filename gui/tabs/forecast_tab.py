from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import QDate
from collections import defaultdict
import pandas as pd
from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord
from logic.tax_utils import get_tax_breakdown
from logic.forecast_service import generate_forecast


class ForecastTab(QWidget):
    """
    Вкладка прогнозування витрат на основі історичних записів.

    Args:
        current_user: Поточний користувач.
        parent: Батьківський віджет.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        layout = QVBoxLayout(self)

        # --- Параметри ---
        params = QHBoxLayout()

        params.addWidget(QLabel("Період навчання з:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addMonths(-12))
        params.addWidget(self.date_start)

        params.addWidget(QLabel("по:"))
        self.date_forecast = QDateEdit()
        self.date_forecast.setCalendarPopup(True)
        self.date_forecast.setDate(QDate.currentDate())
        params.addWidget(self.date_forecast)

        params.addWidget(QLabel("Горизонт (міс):"))
        self.horizon_box = QComboBox()
        self.horizon_box.addItems(["3", "6", "12"])
        self.horizon_box.setCurrentText("6")
        params.addWidget(self.horizon_box)

        self.forecast_btn = QPushButton("Прогнозувати")
        self.forecast_btn.clicked.connect(self.run_forecast)
        params.addWidget(self.forecast_btn)

        layout.addLayout(params)

        # --- Таблиця ---
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels([
            "Місяць", "Без корекції (грн)", "З корекцією (грн)"
        ])
        layout.addWidget(self.result_table)
        self.setLayout(layout)

    def run_forecast(self):
        """
        Збирає дані, формує прогноз та виводить результат у таблицю.
        """
        start_train_date = self.date_start.date().toPyDate()
        start_forecast_date = self.date_forecast.date().toPyDate()
        horizon = int(self.horizon_box.currentText())

        if start_forecast_date <= start_train_date:
            QMessageBox.warning(self, "Помилка", "Дата прогнозу має бути пізніше завершення навчання.")
            return

        try:
            self.result_table.setRowCount(0)
            monthly_data = defaultdict(lambda: {
                "base_salary": 0.0,
                "bonus": 0.0,
                "salary_taxes": 0.0,
                "materials": 0.0,
                "maint_taxes": 0.0
            })

            # --- Збір зарплат ---
            salaries = SalaryRecord.select().where(
                (SalaryRecord.salary_month >= start_train_date) &
                (SalaryRecord.salary_month < start_forecast_date)
            )
            for s in salaries:
                key = s.salary_month.strftime("%Y-%m")
                monthly_data[key]["base_salary"] += float(s.base_salary or 0)
                monthly_data[key]["bonus"] += float(s.bonus or 0)
                monthly_data[key]["salary_taxes"] += sum(float(v) for v in get_tax_breakdown(s).values())

            # --- Збір обслуговування ---
            maints = MaintenanceRecord.select().where(
                (MaintenanceRecord.service_date >= start_train_date) &
                (MaintenanceRecord.service_date < start_forecast_date)
            )
            for m in maints:
                key = m.service_date.strftime("%Y-%m")
                monthly_data[key]["materials"] += float(m.material_cost or 0)
                monthly_data[key]["maint_taxes"] += sum(float(v) for v in get_tax_breakdown(m).values())

            # --- Побудова DataFrame ---
            df = pd.DataFrame([
                {"ds": pd.to_datetime(month + "-01"), "y": sum(data.values())}
                for month, data in sorted(monthly_data.items())
            ])

            if df.empty or len(df) < 3:
                raise ValueError("Недостатньо даних для прогнозу.")

            result_df = generate_forecast(
                df=df,
                start_train_date=start_train_date,
                start_forecast_date=start_forecast_date,
                horizon=horizon,
                apply_seasonality=False  # <-- змінити на False якщо не потрібно
            )

            self.result_table.setRowCount(len(result_df))
            for i, row in result_df.iterrows():
                self.result_table.setItem(i, 0, QTableWidgetItem(row["ds"].strftime("%Y-%m")))
                self.result_table.setItem(i, 1, QTableWidgetItem(f"{row['y']:.2f}"))
                self.result_table.setItem(i, 2, QTableWidgetItem(f"{row['adjusted_y']:.2f}"))

            header = self.result_table.horizontalHeader()
            header.setStretchLastSection(True)
            for col in range(self.result_table.columnCount() - 1):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))
