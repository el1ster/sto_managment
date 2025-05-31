from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QFormLayout, QVBoxLayout
)
from models.employee import Employee
from models.employee_position import EmployeePosition
from models.task import Task
from models.salary_record import SalaryRecord
from models.user import User


class EmployeeCardDialog(QDialog):
    """
    Діалогове вікно для перегляду інформації про працівника.

    Показує:
        - Основну інформацію
        - Задачі
        - Записи по зарплаті
        - Обліковий запис (якщо є)
    """

    def __init__(self, employee, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Картка працівника: {employee.full_name}")
        self.setMinimumSize(520, 400)
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # Основна інформація
        main_tab = QWidget()
        form = QFormLayout()
        form.addRow("ПІБ:", QLabel(employee.full_name))
        form.addRow("Телефон:", QLabel(employee.phone or "-"))
        form.addRow("Email:", QLabel(employee.email or "-"))
        form.addRow("Посада:", QLabel(employee.position.name if employee.position else "-"))
        form.addRow("Дата прийому:", QLabel(str(employee.hire_date) if employee.hire_date else "-"))
        form.addRow("Статус:", QLabel("Активний" if employee.is_active else "Деактивований"))
        main_tab.setLayout(form)
        tabs.addTab(main_tab, "Основне")

        # Всі задачі працівника
        tasks_tab = QWidget()
        tasks_layout = QVBoxLayout()
        try:
            for task in employee.tasks:
                tasks_layout.addWidget(QLabel(
                    f"{task.title} — {task.status} (Дедлайн: {task.deadline})"
                ))
            if not list(employee.tasks):
                tasks_layout.addWidget(QLabel("Задач відсутні."))
        except Exception as ex:
            tasks_layout.addWidget(QLabel(f"Помилка отримання задач: {ex}"))
        tasks_tab.setLayout(tasks_layout)
        tabs.addTab(tasks_tab, "Задачі")

        # Зарплатна інформація
        salary_tab = QWidget()
        salary_layout = QVBoxLayout()
        try:
            records = SalaryRecord.select().where(SalaryRecord.employee == employee)
            for record in records:
                salary_layout.addWidget(QLabel(
                    f"{record.salary_month.strftime('%Y-%m')} — {record.total_payout:.2f} грн"
                ))
            if not records.exists():
                salary_layout.addWidget(QLabel("Записів про зарплату немає."))
        except Exception as ex:
            salary_layout.addWidget(QLabel(f"Помилка завантаження зарплат: {ex}"))
        salary_tab.setLayout(salary_layout)
        tabs.addTab(salary_tab, "Зарплата")

        # Обліковий запис (якщо є)
        user_tab = QWidget()
        user_layout = QFormLayout()
        try:
            user = User.get_or_none(User.employee_id == employee.id)
            if user:
                user_layout.addRow("Логін:", QLabel(user.username))
                user_layout.addRow("Роль:", QLabel(user.role.role_name))
                user_layout.addRow("Активний:", QLabel("Так" if user.is_active else "Ні"))
                user_layout.addRow("Останній вхід:", QLabel(str(user.last_login) if user.last_login else "-"))
            else:
                user_layout.addRow(QLabel("Обліковий запис не створено."))
        except Exception as ex:
            user_layout.addRow(QLabel(f"Помилка пошуку облікового запису: {ex}"))
        user_tab.setLayout(user_layout)
        tabs.addTab(user_tab, "Обліковий запис")

        layout.addWidget(tabs)
