import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QDateEdit, QCheckBox
)
from PyQt6.QtCore import QDate
from models.employee import Employee
from models.employee_position import EmployeePosition
from logic.validators import (
    validate_full_name, validate_phone, validate_email, validate_hire_date
)

class AddEmployeeDialog(QDialog):
    """
    Діалог для додавання нового працівника з суворою валідацією полів.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати працівника")
        self.setFixedSize(350, 360)

        layout = QVBoxLayout()

        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setCalendarPopup(True)
        self.hire_date_edit.setDate(QDate.currentDate())

        self.position_combo = QComboBox()
        self.positions = list(EmployeePosition.select())
        self.position_combo.addItems([p.name for p in self.positions])

        self.active_checkbox = QCheckBox("Активний")
        self.active_checkbox.setChecked(True)

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

        self.save_btn = QPushButton("Додати")
        self.save_btn.clicked.connect(self.add_employee)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)



    def add_employee(self):
        full_name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        email = self.email_edit.text().strip()
        hire_date = self.hire_date_edit.date().toPyDate()
        position = self.positions[self.position_combo.currentIndex()]
        is_active = self.active_checkbox.isChecked()

        if not validate_full_name(full_name, parent=self):
            return
        if not validate_phone(phone, parent=self):
            return
        if not validate_email(email, parent=self):
            return
        if not validate_hire_date(hire_date, parent=self):
            return

        # Перевірка унікальності (email і телефон не повинні дублюватися)
        if Employee.select().where(Employee.email == email).exists():
            QMessageBox.warning(self, "Помилка", "Такий email вже існує в базі працівників.")
            return
        if Employee.select().where(Employee.phone == phone).exists():
            QMessageBox.warning(self, "Помилка", "Такий телефон вже існує в базі працівників.")
            return

        try:
            Employee.create(
                full_name=full_name,
                phone=phone,
                email=email,
                hire_date=hire_date,
                position=position,
                is_active=is_active
            )
            QMessageBox.information(self, "Успіх", "Працівника додано.")
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося додати працівника: {ex}")
