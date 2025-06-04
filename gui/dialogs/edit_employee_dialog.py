from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QDateEdit, QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import QDate
from models.employee import Employee
from models.employee_position import EmployeePosition
from models.user import User
from models.role import UserRole
from logic.password_service import hash_password
from logic.validators import (
    validate_full_name, validate_phone, validate_email, validate_hire_date, validate_username, validate_password
)
from gui.dialogs.password_generator_dialog import PasswordGeneratorDialog


class EditEmployeeDialog(QDialog):
    """
    Діалог для редагування існуючого працівника з можливістю редагування або зміни облікового запису.
    """

    def __init__(self, employee: Employee, current_user, parent=None):
        try:
            super().__init__(parent)
            self.employee = employee
            self.current_user = current_user

            self.setWindowTitle(f"Редагувати працівника: {employee.full_name}")
            self.setFixedSize(380, 780)

            layout = QVBoxLayout()

            self.name_edit = QLineEdit(employee.full_name)
            self.phone_edit = QLineEdit(employee.phone or "")
            self.email_edit = QLineEdit(employee.email or "")
            self.hire_date_edit = QDateEdit()
            self.hire_date_edit.setCalendarPopup(True)
            if employee.hire_date:
                self.hire_date_edit.setDate(
                    QDate(employee.hire_date.year, employee.hire_date.month, employee.hire_date.day))
            else:
                self.hire_date_edit.setDate(QDate.currentDate())

            self.position_combo = QComboBox()
            try:
                self.positions = list(EmployeePosition.select())
                self.position_combo.addItems([pos.name for pos in self.positions])
                for idx, pos in enumerate(self.positions):
                    if pos.id == employee.position.id:
                        self.position_combo.setCurrentIndex(idx)
                        break
            except Exception:
                QMessageBox.critical(self, "Помилка", "Не вдалося завантажити список посад.")
                self.positions = []

            self.active_checkbox = QCheckBox("Активний")
            self.active_checkbox.setChecked(employee.is_active)

            layout.addWidget(QLabel("ПІБ:"))
            layout.addWidget(self.name_edit)
            layout.addWidget(QLabel("Телефон:"))
            phone_layout = QHBoxLayout()
            phone_layout.addWidget(self.phone_edit)

            self.check_phone_btn = QPushButton("🔍")
            self.check_phone_btn.setToolTip("Перевірити та нормалізувати номер")
            self.check_phone_btn.setFixedWidth(32)
            self.check_phone_btn.clicked.connect(self.validate_phone_field)

            phone_layout.addWidget(self.check_phone_btn)
            layout.addLayout(phone_layout)

            layout.addWidget(QLabel("Email:"))
            layout.addWidget(self.email_edit)
            layout.addWidget(QLabel("Дата прийому:"))
            layout.addWidget(self.hire_date_edit)
            layout.addWidget(QLabel("Посада:"))
            layout.addWidget(self.position_combo)
            layout.addSpacing(10)
            layout.addWidget(self.active_checkbox)
            layout.addSpacing(12)

            self.use_existing_checkbox = QCheckBox("Прив’язати до іншої обліковки")
            self.create_account_checkbox = QCheckBox("Створити новий обліковий запис")
            self.use_existing_checkbox.stateChanged.connect(self.sync_checkboxes)
            self.create_account_checkbox.stateChanged.connect(self.sync_checkboxes)
            layout.addWidget(self.use_existing_checkbox)
            layout.addWidget(self.create_account_checkbox)

            # --- Поточна обліковка ---
            self.current_user_label = QLabel("Поточна обліковка:")
            self.current_user_info = QLabel()
            self.update_current_user_info()
            layout.addWidget(self.current_user_label)
            layout.addWidget(self.current_user_info)
            layout.addSpacing(10)

            self.user_label = QLabel("Обліковий запис:")
            self.user_combo = QComboBox()
            try:
                self.active_users = list(User.select().where(User.is_active == True))
                self.user_combo.addItems([u.username for u in self.active_users])
            except Exception:
                QMessageBox.critical(self, "Помилка", "Не вдалося завантажити список користувачів.")
                self.active_users = []

            self.username_label = QLabel("Логін:")
            self.username_edit = QLineEdit()

            self.password_label = QLabel("Пароль:")
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

            self.show_pass_btn = QPushButton("👁")
            self.show_pass_btn.setCheckable(True)
            self.show_pass_btn.setFixedWidth(32)
            self.show_pass_btn.clicked.connect(self.toggle_password_visibility)

            self.gen_pass_btn = QPushButton("🛠")
            self.gen_pass_btn.setFixedWidth(32)
            self.gen_pass_btn.clicked.connect(self.open_password_generator)

            pass_layout = QHBoxLayout()
            pass_layout.addWidget(self.password_edit)
            pass_layout.addWidget(self.show_pass_btn)
            pass_layout.addWidget(self.gen_pass_btn)

            self.role_label = QLabel("Роль:")
            self.role_combo = QComboBox()
            self.load_roles()

            layout.addWidget(self.user_label)
            layout.addWidget(self.user_combo)
            layout.addWidget(self.username_label)
            layout.addWidget(self.username_edit)
            layout.addWidget(self.password_label)
            layout.addLayout(pass_layout)
            layout.addWidget(self.role_label)
            layout.addWidget(self.role_combo)

            self.user_label.hide()
            self.user_combo.hide()
            self.username_label.hide()
            self.username_edit.hide()
            self.password_label.hide()
            self.password_edit.hide()
            self.show_pass_btn.hide()
            self.gen_pass_btn.hide()
            self.role_label.hide()
            self.role_combo.hide()

            self.save_btn = QPushButton("Зберегти зміни")
            self.save_btn.clicked.connect(self.save_employee)
            layout.addWidget(self.save_btn)

            self.setLayout(layout)

        except Exception as e:
            QMessageBox.critical(None, "Помилка", f"Не вдалося ініціалізувати вікно: {e}")

    def update_current_user_info(self):
        try:
            if self.employee.user:
                info = f"<b>{self.employee.user.username}</b> — {self.employee.user.role.role_name}"
                if not self.employee.user.is_active:
                    info += " (неактивна)"
                self.current_user_info.setText(info)
            else:
                self.current_user_info.setText("Обліковка не прив’язана.")
        except Exception:
            self.current_user_info.setText("Помилка при отриманні обліковки.")

    def toggle_password_visibility(self):
        try:
            if self.show_pass_btn.isChecked():
                self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
                self.show_pass_btn.setText("❌")
            else:
                self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
                self.show_pass_btn.setText("👁")
        except Exception:
            QMessageBox.warning(self, "Помилка", "Не вдалося перемкнути видимість пароля.")

    def open_password_generator(self):
        try:
            dlg = PasswordGeneratorDialog(min_length=8, parent=self)
            dlg.password_generated.connect(self.password_edit.setText)
            dlg.exec()
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося відкрити генератор паролів.")

    def sync_checkboxes(self):
        try:
            if self.sender() == self.use_existing_checkbox and self.use_existing_checkbox.isChecked():
                self.create_account_checkbox.setChecked(False)
            elif self.sender() == self.create_account_checkbox and self.create_account_checkbox.isChecked():
                self.use_existing_checkbox.setChecked(False)
            self.update_account_fields()
        except Exception:
            QMessageBox.warning(self, "Помилка", "Не вдалося оновити стан прапорців.")

    def update_account_fields(self):
        try:
            use_existing = self.use_existing_checkbox.isChecked()
            create_new = self.create_account_checkbox.isChecked()

            self.user_label.setVisible(use_existing)
            self.user_combo.setVisible(use_existing)

            self.username_label.setVisible(create_new)
            self.username_edit.setVisible(create_new)
            self.password_label.setVisible(create_new)
            self.password_edit.setVisible(create_new)
            self.show_pass_btn.setVisible(create_new)
            self.gen_pass_btn.setVisible(create_new)
            self.role_label.setVisible(create_new)
            self.role_combo.setVisible(create_new)
        except Exception:
            QMessageBox.warning(self, "Помилка", "Не вдалося оновити поля обліковки.")

    def load_roles(self):
        try:
            self.role_combo.clear()
            if self.current_user.role.role_name == "superadmin":
                roles = UserRole.select()
            else:
                roles = UserRole.select().where(UserRole.role_name.not_in(["superadmin", "admin", "owner"]))
            self.role_combo.addItems([r.role_name for r in roles])
            self.allowed_roles = list(roles)
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося завантажити ролі.")
            self.allowed_roles = []

    def save_employee(self):
        try:
            full_name = self.name_edit.text().strip()
            phone = self.phone_edit.text().strip()
            email = self.email_edit.text().strip()
            hire_date = self.hire_date_edit.date().toPyDate()
            position = self.positions[self.position_combo.currentIndex()]
            is_active = self.active_checkbox.isChecked()

            if not validate_full_name(full_name, parent=self): return
            if not validate_phone(phone, parent=self): return
            if not validate_email(email, parent=self): return
            if not validate_hire_date(hire_date, parent=self): return

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

            user = self.employee.user
            if self.create_account_checkbox.isChecked():
                username = self.username_edit.text().strip()
                password = self.password_edit.text().strip()
                role_name = self.role_combo.currentText()

                if not validate_username(username, parent=self):
                    return
                if not validate_password(password, parent=self):
                    return
                if User.select().where(User.username == username).exists():
                    QMessageBox.warning(self, "Помилка", "Такий логін вже існує.")
                    return

                user = User.create(
                    username=username,
                    password_hash=hash_password(password),
                    role=UserRole.get(UserRole.role_name == role_name)
                )
            elif self.use_existing_checkbox.isChecked():
                user = self.active_users[self.user_combo.currentIndex()]

            self.employee.full_name = full_name
            self.employee.phone = phone
            self.employee.email = email
            self.employee.hire_date = hire_date
            self.employee.position = position
            self.employee.is_active = is_active
            self.employee.user = user
            self.employee.save()

            QMessageBox.information(self, "Успіх", "Дані працівника оновлено.")
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити працівника: {ex}")

    def validate_phone_field(self):
        """
        Перевіряє правильність та нормалізує телефон.
        """
        phone = self.phone_edit.text().strip()
        validate_phone(phone, parent=self)
