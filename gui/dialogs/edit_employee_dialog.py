from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QDateEdit, QCheckBox
)
from PyQt6.QtCore import QDate
from models.employee import Employee
from models.employee_position import EmployeePosition
from logic.validators import (
    validate_full_name, validate_phone, validate_email, validate_hire_date
)

class EditEmployeeDialog(QDialog):
    """
    Діалог для редагування існуючого працівника.
    """

    def __init__(self, employee: Employee, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.setWindowTitle(f"Редагувати працівника: {employee.full_name}")
        self.setFixedSize(350, 360)

        layout = QVBoxLayout()

        self.name_edit = QLineEdit(employee.full_name)
        self.phone_edit = QLineEdit(employee.phone or "")
        self.email_edit = QLineEdit(employee.email or "")

        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setCalendarPopup(True)
        # Встановлюємо дату прийому (або поточну, якщо не задана)
        if employee.hire_date:
            self.hire_date_edit.setDate(QDate(employee.hire_date.year, employee.hire_date.month, employee.hire_date.day))
        else:
            self.hire_date_edit.setDate(QDate.currentDate())

        self.position_combo = QComboBox()
        self.positions = list(EmployeePosition.select())
        for pos in self.positions:
            self.position_combo.addItem(pos.name)
        # Встановлюємо поточну посаду
        current_index = 0
        for idx, pos in enumerate(self.positions):
            if pos.id == employee.position.id:
                current_index = idx
                break
        self.position_combo.setCurrentIndex(current_index)

        self.active_checkbox = QCheckBox("Активний")
        self.active_checkbox.setChecked(employee.is_active)

        layout.addWidget(QLabel("ПІБ:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Телефон:"))
        layout.addWidget(self.phone_edit)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Дата прийому:"))
        layout.addWidget(self.hire_date_edit)
        layout.addWidget(QLabel("Посада:"))
        layout.addWidget(self.position_combo)
        layout.addWidget(self.active_checkbox)

        self.save_btn = QPushButton("Зберегти зміни")
        self.save_btn.clicked.connect(self.save_employee)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    def save_employee(self):
        full_name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        email = self.email_edit.text().strip()
        hire_date = self.hire_date_edit.date().toPyDate()
        position = self.positions[self.position_combo.currentIndex()]
        is_active = self.active_checkbox.isChecked()

        # Валідація
        if not validate_full_name(full_name, parent=self):
            return
        if not validate_phone(phone, parent=self):
            return
        if not validate_email(email, parent=self):
            return
        if not validate_hire_date(hire_date, parent=self):
            return

        # Перевірка унікальності (email і телефон не повинні дублюватися у інших)
        from models.employee import Employee
        exists_email = Employee.select().where(
            (Employee.email == email) & (Employee.id != self.employee.id)
        ).exists()
        if exists_email:
            QMessageBox.warning(self, "Помилка", "Такий email вже існує в базі працівників.")
            return

        exists_phone = Employee.select().where(
            (Employee.phone == phone) & (Employee.id != self.employee.id)
        ).exists()
        if exists_phone:
            QMessageBox.warning(self, "Помилка", "Такий телефон вже існує в базі працівників.")
            return

        # Збереження
        try:
            self.employee.full_name = full_name
            self.employee.phone = phone
            self.employee.email = email
            self.employee.hire_date = hire_date
            self.employee.position = position
            self.employee.is_active = is_active
            self.employee.save()
            QMessageBox.information(self, "Успіх", "Дані працівника оновлено.")
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити працівника: {ex}")
