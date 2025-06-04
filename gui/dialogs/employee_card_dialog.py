from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QFormLayout
)
from models.employee import Employee
from models.salary_record import SalaryRecord
from models.user import User
from models.optimization_worker import OptimizationWorker
from models.assignment import Assignment
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from gui.dialogs.task_card_dialog import TaskCardDialog
from gui.dialogs.salary_card_dialog import SalaryCardDialog


class EmployeeCardDialog(QDialog):
    """
    Діалогове вікно для перегляду інформації про працівника.

    Показує:
        - Основну інформацію
        - Задачі
        - Записи по зарплаті
        - Обліковий запис (якщо є)
    """

    def __init__(self, employee: Employee, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Картка працівника: {employee.full_name}")
        self.setMinimumSize(520, 400)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # --- Основна інформація ---
        try:
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
        except Exception as e:
            error_tab = QWidget()
            error_layout = QVBoxLayout()
            error_layout.addWidget(QLabel(f"Помилка завантаження основної інформації: {e}"))
            error_tab.setLayout(error_layout)
            tabs.addTab(error_tab, "Основне")

        # --- Задачі ---
        tasks_tab = QWidget()
        try:
            worker = OptimizationWorker.get_or_none(OptimizationWorker.employee == employee)
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Назва", "Статус", "ID"])
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            if worker:
                assignments = Assignment.select().where(Assignment.worker == worker)
                tasks = [a.task for a in assignments]
                table.setRowCount(len(tasks))
                for i, task in enumerate(tasks):
                    table.setItem(i, 0, QTableWidgetItem(task.name))
                    table.setItem(i, 1, QTableWidgetItem(task.status))
                    table.setItem(i, 2, QTableWidgetItem(str(task.id)))
                table.cellDoubleClicked.connect(lambda row, col: self.open_task_card(tasks[row]))
            else:
                table.setRowCount(1)
                table.setItem(0, 0, QTableWidgetItem("Цей працівник не зареєстрований як виконавець."))

            tasks_tab.setLayout(QVBoxLayout())
            tasks_tab.layout().addWidget(table)
        except Exception as ex:
            tasks_tab.setLayout(QVBoxLayout())
            tasks_tab.layout().addWidget(QLabel(f"Помилка отримання задач: {ex}"))

        tabs.addTab(tasks_tab, "Задачі")

        # --- Зарплата ---
        salary_tab = QWidget()
        try:
            records = list(SalaryRecord.select().where(SalaryRecord.employee == employee))
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Місяць", "Базова", "Бонус", "Разом"])
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            table.setRowCount(len(records))
            for i, record in enumerate(records):
                table.setItem(i, 0, QTableWidgetItem(record.salary_month.strftime('%Y-%m')))
                table.setItem(i, 1, QTableWidgetItem(f"{record.base_salary:.2f}"))
                table.setItem(i, 2, QTableWidgetItem(f"{record.bonus:.2f}"))
                table.setItem(i, 3, QTableWidgetItem(f"{(record.base_salary + record.bonus):.2f}"))

            table.cellDoubleClicked.connect(lambda row, col: self.open_salary_card(records[row]))
            salary_tab.setLayout(QVBoxLayout())
            salary_tab.layout().addWidget(table)
        except Exception as ex:
            salary_tab.setLayout(QVBoxLayout())
            salary_tab.layout().addWidget(QLabel(f"Помилка завантаження зарплат: {ex}"))

        tabs.addTab(salary_tab, "Зарплата")

        # --- Обліковий запис ---
        user_tab = QWidget()
        user_layout = QFormLayout()
        try:
            user = employee.user  # <-- Ось правильне місце отримання
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

    def open_task_card(self, task):
        try:
            dlg = TaskCardDialog(task, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити задачу: {e}")

    def open_salary_card(self, record):
        try:
            dlg = SalaryCardDialog(record, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити зарплатну операцію: {e}")
