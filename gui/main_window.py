from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QApplication
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
        self.logout_requested = False
        print(f"[MainWindow] Ініціалізація для користувача: {self.current_user.username}")
        self.setWindowTitle(config.APP_NAME)
        self.resize(*config.DEFAULT_WINDOW_SIZE)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Додаємо вкладки згідно прав (приклад для супер-адміна)
        self.tab_widget.addTab(UsersTab(self.current_user, main_window=self), "Користувачі")
        self.tab_widget.addTab(EmployeesTab(self.current_user, main_window=self), "Працівники")
        self.tab_widget.addTab(FinanceTab(self.current_user, main_window=self), "Фінанси")
        self.tab_widget.addTab(VehiclesTab(self.current_user, main_window=self), "Транспорт")
        self.tab_widget.addTab(TasksTab(self.current_user, main_window=self), "Задачі")
        self.tab_widget.addTab(OptimizationTab(self.current_user, main_window=self), "Оптимізація")
        self.tab_widget.addTab(PartsTab(self.current_user, main_window=self), "Запчастини")
        self.tab_widget.addTab(LogsTab(self.current_user, main_window=self), "Логи")

        print("[MainWindow] Всі вкладки додані.")

        # Додаємо індикатор користувача у status bar
        self.statusBar().showMessage(
            f"Ви ввійшли як: {self.current_user.username} ({self.current_user.role.role_name})"
        )

    def closeEvent(self, event):
        print("[MainWindow] Викликано closeEvent.")
        msg = QMessageBox(self)
        msg.setWindowTitle("Підтвердження")
        msg.setText("Що ви хочете зробити?")
        logout_btn = msg.addButton("Вийти з профілю", QMessageBox.ButtonRole.ActionRole)
        quit_btn = msg.addButton("Закрити", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg.addButton("Скасувати", QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(logout_btn)
        msg.exec()

        if msg.clickedButton() == logout_btn:
            print("[MainWindow] Користувач обрав: Вийти з облікового запису.")
            self.logout_requested = True
            event.accept()  # Закриваємо це вікно (app.exec() завершиться)
            print("[MainWindow] MainWindow закривається через logout.")
            QApplication.quit()  # Явно завершуємо event loop
        elif msg.clickedButton() == quit_btn:
            print("[MainWindow] Користувач обрав: Закрити програму.")
            self.logout_requested = False
            event.accept()
            print("[MainWindow] MainWindow закривається повністю.")
        else:
            print("[MainWindow] Користувач обрав: Скасувати.")
            event.ignore()

    def update_user_status(self):
        self.statusBar().showMessage(
            f"Ви ввійшли як: {self.current_user.username} ({self.current_user.role.role_name})"
        )

