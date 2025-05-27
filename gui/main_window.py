# gui/main_window.py

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication
from gui.tabs.users_tab import UsersTab
from gui.tabs.employees_tab import EmployeesTab
from gui.tabs.finance_tab import FinanceTab
from gui.tabs.vehicles_tab import VehiclesTab
from gui.tabs.tasks_tab import TasksTab
from gui.tabs.optimization_tab import OptimizationTab
from gui.tabs.parts_tab import PartsTab
from gui.tabs.logs_tab import LogsTab

import config


class MainWindow(QMainWindow):
    """
    Головне вікно додатку з вкладками для кожного модуля.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.resize(*config.DEFAULT_WINDOW_SIZE)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Додаємо вкладки (для superadmin — усі доступні)
        self.tab_widget.addTab(UsersTab(), "Користувачі")
        self.tab_widget.addTab(EmployeesTab(), "Працівники")
        self.tab_widget.addTab(FinanceTab(), "Фінанси")
        self.tab_widget.addTab(VehiclesTab(), "Транспорт")
        self.tab_widget.addTab(TasksTab(), "Задачі")
        self.tab_widget.addTab(OptimizationTab(), "Оптимізація")
        self.tab_widget.addTab(PartsTab(), "Запчастини")
        self.tab_widget.addTab(LogsTab(), "Логи")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
