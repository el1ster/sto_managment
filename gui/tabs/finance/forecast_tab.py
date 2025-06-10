from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QCheckBox
)
from PyQt6.QtCore import QDate
from collections import defaultdict
import pandas as pd
from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord
from logic.tax_utils import get_tax_breakdown
from logic.forecast_service import generate_forecast
from config import ENTERPRISE_START_DATE


class ForecastTab(QWidget):
    """
    Вкладка прогнозування витрат на основі історичних записів.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.seasonal_coeffs = {}

        layout = QVBoxLayout(self)

        # --- Параметри ---
        params = QHBoxLayout()

        params.addWidget(QLabel("Період навчання з:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate(ENTERPRISE_START_DATE.year, ENTERPRISE_START_DATE.month, ENTERPRISE_START_DATE.day))
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

        self.seasonal_checkbox = QCheckBox("Використовувати сезонні коефіцієнти")
        self.seasonal_checkbox.setChecked(False)
        params.addWidget(self.seasonal_checkbox)

        self.forecast_btn = QPushButton("Прогнозувати")
        self.forecast_btn.clicked.connect(self.run_forecast)
        params.addWidget(self.forecast_btn)

        self.show_coeffs_btn = QPushButton("Показати коефіцієнти")
        self.show_coeffs_btn.setEnabled(False)
        self.show_coeffs_btn.clicked.connect(self.show_seasonal_coefficients)
        params.addWidget(self.show_coeffs_btn)

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
        use_seasonality = self.seasonal_checkbox.isChecked()

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

            salaries = SalaryRecord.select().where(
                (SalaryRecord.salary_month >= start_train_date) &
                (SalaryRecord.salary_month < start_forecast_date)
            )
            for s in salaries:
                key = s.salary_month.strftime("%Y-%m")
                monthly_data[key]["base_salary"] += float(s.base_salary or 0)
                monthly_data[key]["bonus"] += float(s.bonus or 0)
                monthly_data[key]["salary_taxes"] += sum(float(v) for v in get_tax_breakdown(s).values())

            maints = MaintenanceRecord.select().where(
                (MaintenanceRecord.service_date >= start_train_date) &
                (MaintenanceRecord.service_date < start_forecast_date)
            )
            for m in maints:
                key = m.service_date.strftime("%Y-%m")
                monthly_data[key]["materials"] += float(m.material_cost or 0)
                monthly_data[key]["maint_taxes"] += sum(float(v) for v in get_tax_breakdown(m).values())

            df = pd.DataFrame([
                {"ds": pd.to_datetime(month + "-01"), "y": sum(data.values())}
                for month, data in sorted(monthly_data.items())
            ])

            if df.empty or len(df) < 3:
                raise ValueError("Недостатньо даних для прогнозу.")

            result_df, self.seasonal_coeffs = generate_forecast(
                df=df,
                start_train_date=start_train_date,
                start_forecast_date=start_forecast_date,
                horizon=horizon,
                apply_seasonality=use_seasonality
            )

            self.result_table.setRowCount(len(result_df))
            for i, row in result_df.iterrows():
                self.result_table.setItem(i, 0, QTableWidgetItem(row["ds"].strftime("%Y-%m")))
                self.result_table.setItem(i, 1, QTableWidgetItem(f"{row['y']:.2f}"))
                self.result_table.setItem(i, 2, QTableWidgetItem(f"{row['adjusted_y']:.2f}"))

            self.show_coeffs_btn.setEnabled(use_seasonality)

            header = self.result_table.horizontalHeader()
            header.setStretchLastSection(True)
            for col in range(self.result_table.columnCount() - 1):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def show_seasonal_coefficients(self):
        """
        Відображає таблицю сезонних коефіцієнтів.
        """
        if not self.seasonal_coeffs:
            QMessageBox.information(self, "Інформація", "Сезонні коефіцієнти відсутні.")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Сезонні коефіцієнти")
        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Місяць", "Коефіцієнт"])
        table.setRowCount(12)

        for i in range(1, 13):
            coeff = self.seasonal_coeffs.get(i, 1.0)
            table.setItem(i - 1, 0, QTableWidgetItem(str(i)))
            table.setItem(i - 1, 1, QTableWidgetItem(f"{coeff:.4f}"))

        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.setMinimumSize(300, 410)
        dialog.exec()
