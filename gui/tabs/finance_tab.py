from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from gui.tabs.accounting_table import AccountingTab
# from gui.tabs.employee_expenses import EmployeeExpensesTab
# from gui.tabs.vehicle_expenses import VehicleExpensesTab
# from gui.tabs.tax_view import TaxViewTab
# from gui.tabs.forecast import ForecastTab
from gui.tabs.tax_view import TaxViewTab


class FinanceTab(QWidget):
    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window  # зберігаємо для можливого використання


        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.tabs.addTab(AccountingTab(current_user), "Усі витрати")
        self.tabs.addTab(TaxViewTab(current_user), "Податки")
        # self.tabs.addTab(EmployeeExpensesTab(current_user), "По працівниках")
        # self.tabs.addTab(VehicleExpensesTab(current_user), "По автомобілях")
        # self.tabs.addTab(TaxViewTab(current_user), "Податки")
        # self.tabs.addTab(ForecastTab(), "Прогноз")

        layout.addWidget(self.tabs)
        self.setLayout(layout)
