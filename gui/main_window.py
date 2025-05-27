# gui/main_window.py

from PyQt6.QtWidgets import QMainWindow, QTabWidget
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
    Приймає current_user для контролю доступу.
    """

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle(config.APP_NAME)
        self.resize(*config.DEFAULT_WINDOW_SIZE)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Додаємо вкладки згідно прав (приклад для супер-адміна)
        self.tab_widget.addTab(UsersTab(self.current_user), "Користувачі")
        self.tab_widget.addTab(EmployeesTab(self.current_user), "Працівники")
        self.tab_widget.addTab(FinanceTab(self.current_user), "Фінанси")
        self.tab_widget.addTab(VehiclesTab(self.current_user), "Транспорт")
        self.tab_widget.addTab(TasksTab(self.current_user), "Задачі")
        self.tab_widget.addTab(OptimizationTab(self.current_user), "Оптимізація")
        self.tab_widget.addTab(PartsTab(self.current_user), "Запчастини")
        self.tab_widget.addTab(LogsTab(self.current_user), "Логи")
