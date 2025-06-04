from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox
)
from models.user import User
from models.employee import Employee
from gui.dialogs.add_employee_dialog import AddEmployeeDialog
from gui.dialogs.employee_card_dialog import EmployeeCardDialog
from gui.dialogs.select_employee_dialog import SelectEmployeeDialog
from models.assignment import Assignment
from models.salary_record import SalaryRecord
from models.optimization_worker import OptimizationWorker



class UserCardDialog(QDialog):
    """
    Діалогове вікно для перегляду даних користувача та його працівників.

    Args:
        user (User): Об'єкт користувача.
        current_user: Поточний користувач (для контролю доступу).
        parent: Батьківське вікно.
    """

    def __init__(self, user: User, current_user: User, parent=None):
        super().__init__(parent)
        self.user = user
        self.current_user = current_user

        self.setWindowTitle(f"Обліковий запис: {user.username}")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # --- Інформація про користувача ---
        layout.addWidget(QLabel(f"<b>Логін:</b> {user.username}"))
        layout.addWidget(QLabel(f"<b>Роль:</b> {user.role.role_name}"))
        layout.addWidget(QLabel(f"<b>Активний:</b> {'Так' if user.is_active else 'Ні'}"))
        layout.addWidget(QLabel(f"<b>Останній вхід:</b> {user.last_login or '-'}"))

        # --- Прив’язані працівники ---
        layout.addWidget(QLabel("<b>Пов’язані працівники:</b>"))
        self.employee_list = QListWidget()
        try:
            employees = Employee.select().where(Employee.user == user)
            if employees:
                for emp in employees:
                    self.employee_list.addItem(f"{emp.full_name} ({emp.position.name})")
            else:
                self.employee_list.addItem("Немає прив’язаних працівників.")
        except Exception as e:
            self.employee_list.addItem(f"Помилка: {e}")
        self.employee_list.itemDoubleClicked.connect(self.open_employee_card)
        layout.addWidget(self.employee_list)

        # --- Кнопки ---
        self.add_existing_btn = QPushButton("Прив’язати існуючого працівника")
        self.add_existing_btn.clicked.connect(self.add_existing_employee)

        self.create_new_btn = QPushButton("Створити нового працівника")
        self.create_new_btn.clicked.connect(self.create_new_employee)


        layout.addWidget(self.add_existing_btn)
        layout.addWidget(self.create_new_btn)

        self.setLayout(layout)

    def add_existing_employee(self):
        try:
            dlg = SelectEmployeeDialog(self)
            if dlg.exec():
                emp = dlg.selected_employee
                emp.user = self.user
                emp.save()
                QMessageBox.information(self, "Успіх", f"Працівника {emp.full_name} прив’язано.")
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося прив’язати працівника: {e}")

    def create_new_employee(self):
        try:
            dlg = AddEmployeeDialog(current_user=self.current_user, parent=self)
            if dlg.exec():
                QMessageBox.information(self, "Успіх", "Працівника створено та прив’язано.")
                self.close()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити працівника: {e}")

    def open_employee_card(self, item):
        """
        Відкриває картку працівника при подвійному кліку по списку.
        """
        try:
            full_text = item.text()
            if "(" not in full_text:
                return  # Системні повідомлення типу "Немає працівників" ігноруємо

            emp_name = full_text.split(" (")[0].strip()
            employee = Employee.get_or_none(
                (Employee.user == self.user) & (Employee.full_name == emp_name)
            )
            if employee:
                from gui.dialogs.employee_card_dialog import EmployeeCardDialog
                dlg = EmployeeCardDialog(employee, parent=self)
                dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити працівника: {e}")

