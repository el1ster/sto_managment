from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QApplication
from gui.tabs.users_tab import UsersTab
from gui.tabs.employees_tab import EmployeesTab
from gui.tabs.finance_tab import FinanceTab
from gui.tabs.tasks_tab import TasksTab
from gui.tabs.optimization_tab import OptimizationTab
from gui.tabs.logs_tab import LogsTab
from gui.tabs.transport_tab import TransportTab

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

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

        try:
            self.setWindowTitle(config.APP_NAME)
            self.resize(*config.DEFAULT_WINDOW_SIZE)

            self.tab_widget = QTabWidget(self)
            self.setCentralWidget(self.tab_widget)

            self.tab_widget.addTab(UsersTab(self.current_user, main_window=self), "Користувачі")
            self.tab_widget.addTab(EmployeesTab(self.current_user, main_window=self), "Працівники")
            self.tab_widget.addTab(TransportTab(self.current_user, main_window=self), "Транспорт")  # <-- НОВА ВКЛАДКА
            self.tab_widget.addTab(FinanceTab(self.current_user, main_window=self), "Фінанси")
            self.tab_widget.addTab(TasksTab(self.current_user, main_window=self), "Задачі")
            self.tab_widget.addTab(OptimizationTab(self.current_user, main_window=self), "Оптимізація")
            # self.tab_widget.addTab(PartsTab(self.current_user, main_window=self), "Запчастини")
            self.tab_widget.addTab(LogsTab(self.current_user, main_window=self), "Логи")

            self.statusBar().showMessage(
                f"Ви ввійшли як: {self.current_user.username} ({self.current_user.role.role_name})"
            )

        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося ініціалізувати інтерфейс:\n{ex}")

    def closeEvent(self, event):
        try:
            msg = QMessageBox(self)
            msg.setWindowTitle("Підтвердження")
            msg.setText("Що ви хочете зробити?")
            logout_btn = msg.addButton("Вийти з профілю", QMessageBox.ButtonRole.ActionRole)
            quit_btn = msg.addButton("Закрити", QMessageBox.ButtonRole.DestructiveRole)
            cancel_btn = msg.addButton("Скасувати", QMessageBox.ButtonRole.RejectRole)
            msg.setDefaultButton(logout_btn)
            msg.exec()

            if msg.clickedButton() == logout_btn:
                self.logout_requested = True
                event.accept()
                QApplication.quit()
            elif msg.clickedButton() == quit_btn:
                self.logout_requested = False
                event.accept()
            else:
                event.ignore()
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося виконати закриття:\n{ex}")
            event.ignore()

    def update_user_status(self):
        try:
            self.statusBar().showMessage(
                f"Ви ввійшли як: {self.current_user.username} ({self.current_user.role.role_name})"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити статус користувача:\n{ex}")
