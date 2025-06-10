from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel

from gui.tabs.finance.accounting_table import AccountingTab
from gui.tabs.finance.tax_tab import TaxViewTab
from gui.tabs.finance.salaries_tab import SalariesTab
from gui.tabs.finance.maintenance_tab import MaintenanceTab
from gui.tabs.finance.forecast_tab import ForecastTab


class FinanceTab(QWidget):
    """
    Головна вкладка 'Фінанси' з підвкладками:
    - Облік витрат
    - Зарплати
    - Обслуговування
    - Податки
    """

    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # --- Усі витрати ---
        try:
            self.tabs.addTab(AccountingTab(current_user), "Усі витрати")
        except Exception as e:
            self.tabs.addTab(self._error_tab(f"Не вдалося завантажити облік: {e}"), "Усі витрати")

        # --- Зарплати ---
        try:
            self.salaries_tab = SalariesTab(current_user=self.current_user, parent=self)
            self.tabs.addTab(self.salaries_tab, "Зарплати")
        except Exception as e:
            self.tabs.addTab(self._error_tab(f"Помилка у вкладці 'Зарплати': {e}"), "Зарплати")

        # --- Обслуговування ---
        try:
            self.maintenance_tab = MaintenanceTab(current_user=self.current_user, parent=self)
            self.tabs.addTab(self.maintenance_tab, "Обслуговування")
        except Exception as e:
            self.tabs.addTab(self._error_tab(f"Помилка у вкладці 'Обслуговування': {e}"), "Обслуговування")

        # --- Податки ---
        try:
            self.tabs.addTab(TaxViewTab(current_user), "Податки")
        except Exception as e:
            self.tabs.addTab(self._error_tab(f"Не вдалося завантажити податки: {e}"), "Податки")

        try:
            self.tabs.addTab(ForecastTab(current_user), "Прогноз")
        except Exception as e:
            self.tabs.addTab(self._error_tab(f"Помилка прогнозу: {e}"), "Прогноз")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def _error_tab(self, message: str) -> QWidget:
        """
        Створює вкладку з повідомленням про помилку.

        Args:
            message (str): Текст повідомлення.

        Returns:
            QWidget: Віджет-вкладка з повідомленням.
        """
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        tab.setLayout(layout)
        return tab
