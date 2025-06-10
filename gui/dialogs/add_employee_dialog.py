from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QDateEdit, QCheckBox, QHBoxLayout, QSpinBox
)
from PyQt6.QtCore import QDate
from models.employee import Employee
from models.employee_position import EmployeePosition
from models.user import User
from models.role import UserRole
from models.optimization_worker import OptimizationWorker
from logic.password_service import hash_password
from logic.validators import (
    validate_full_name, validate_phone, validate_email, validate_hire_date, validate_username, validate_password
)
from gui.dialogs.password_generator_dialog import PasswordGeneratorDialog
from config import SPECIALIZATIONS
from logic.validators import validate_specialization, validate_max_hours


class AddEmployeeDialog(QDialog):
    """
    Діалог для додавання нового працівника з можливістю створення або прив’язки обліковки.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        try:
            self.setWindowTitle("Додати працівника")
            self.setFixedSize(400, 660)

            layout = QVBoxLayout()

            self.name_edit = QLineEdit()
            self.phone_edit = QLineEdit()
            self.email_edit = QLineEdit()
            self.hire_date_edit = QDateEdit()
            self.hire_date_edit.setCalendarPopup(True)
            self.hire_date_edit.setDate(QDate.currentDate())

            self.position_combo = QComboBox()
            self.positions = list(EmployeePosition.select())
            self.position_combo.addItem("-- Оберіть посаду --")  # Порожній пункт
            self.position_combo.addItems([p.name for p in self.positions])
            self.position_combo.currentIndexChanged.connect(self.on_position_changed)

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

            # --- Оптимізаційні поля ---
            self.specialization_combo = QComboBox()
            self.specialization_combo.addItems(SPECIALIZATIONS)
            self.qualification_input = QSpinBox()
            self.qualification_input.setRange(1, 5)
            self.qualification_input.setValue(3)
            self.qualification_input.setEnabled(False)
            self.max_hours_edit = QLineEdit()
            self.max_hours_edit.setPlaceholderText("годин на день")

            self.specialization_combo.setEnabled(False)
            self.max_hours_edit.setEnabled(False)

            self.use_existing_checkbox = QCheckBox("Прив’язати до існуючої обліковки")
            self.create_account_checkbox = QCheckBox("Створити новий обліковий запис")
            self.use_existing_checkbox.stateChanged.connect(self.sync_checkboxes)
            self.create_account_checkbox.stateChanged.connect(self.sync_checkboxes)
            layout.addWidget(self.use_existing_checkbox)
            layout.addWidget(self.create_account_checkbox)

            self.user_combo = QComboBox()
            self.active_users = list(User.select().where(User.is_active == True))
            self.user_combo.addItems([u.username for u in self.active_users])
            self.user_label = QLabel("Обліковий запис:")

            self.username_edit = QLineEdit()
            self.username_label = QLabel("Логін:")

            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_label = QLabel("Пароль:")

            password_layout = QHBoxLayout()
            self.gen_password_btn = QPushButton("🔧")
            self.gen_password_btn.setFixedWidth(32)
            self.gen_password_btn.setToolTip("Згенерувати пароль")
            self.gen_password_btn.clicked.connect(self.open_password_generator)

            self.show_password_btn = QPushButton("👁")
            self.show_password_btn.setCheckable(True)
            self.show_password_btn.setFixedWidth(32)
            self.show_password_btn.setToolTip("Показати/сховати пароль")
            self.show_password_btn.clicked.connect(self.toggle_password_visibility)

            self.specialization_label = QLabel("Спеціалізація (для механіка/майстра):")
            self.qualification_label = QLabel("Кваліфікація:")
            self.max_hours_label = QLabel("Максимальне навантаження (год/день):")

            password_layout.addWidget(self.password_edit)
            password_layout.addWidget(self.gen_password_btn)
            password_layout.addWidget(self.show_password_btn)

            self.role_combo = QComboBox()
            self.role_label = QLabel("Роль:")
            self.load_roles()

            layout.addWidget(self.user_label)
            layout.addWidget(self.user_combo)
            layout.addWidget(self.username_label)
            layout.addWidget(self.username_edit)
            layout.addWidget(self.password_label)
            layout.addLayout(password_layout)
            layout.addWidget(self.role_label)
            layout.addWidget(self.role_combo)

            layout.addWidget(self.specialization_label)
            layout.addWidget(self.specialization_combo)
            layout.addWidget(self.max_hours_label)
            layout.addWidget(self.max_hours_edit)

            self.user_label.hide()
            self.user_combo.hide()
            self.username_label.hide()
            self.username_edit.hide()
            self.password_label.hide()
            self.password_edit.hide()
            self.gen_password_btn.hide()
            self.show_password_btn.hide()
            self.role_label.hide()
            self.role_combo.hide()
            layout.addWidget(self.qualification_label)
            layout.addWidget(self.qualification_input)
            self.save_btn = QPushButton("Додати")
            self.save_btn.clicked.connect(self.add_employee)
            layout.addWidget(self.save_btn)

            self.specialization_label.setEnabled(False)
            self.specialization_combo.setEnabled(False)
            self.max_hours_label.setEnabled(False)
            self.max_hours_edit.setEnabled(False)
            self.qualification_label.setEnabled(False)
            self.qualification_input.setEnabled(False)

            self.setLayout(layout)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка ініціалізації форми: {e}")

    def on_position_changed(self):
        index = self.position_combo.currentIndex()
        if index == 0:
            self.specialization_label.setEnabled(False)
            self.specialization_combo.setEnabled(False)
            self.max_hours_label.setEnabled(False)
            self.max_hours_edit.setEnabled(False)
            return

        selected_position = self.positions[index - 1].name.lower()
        is_mech_or_master = selected_position in ["механік", "майстер"]

        self.specialization_label.setEnabled(is_mech_or_master)
        self.specialization_combo.setEnabled(is_mech_or_master)
        self.max_hours_label.setEnabled(is_mech_or_master)
        self.max_hours_edit.setEnabled(is_mech_or_master)
        self.qualification_label.setEnabled(is_mech_or_master)
        self.qualification_input.setEnabled(is_mech_or_master)

    def sync_checkboxes(self):
        if self.sender() == self.use_existing_checkbox and self.use_existing_checkbox.isChecked():
            self.create_account_checkbox.setChecked(False)
        elif self.sender() == self.create_account_checkbox and self.create_account_checkbox.isChecked():
            self.use_existing_checkbox.setChecked(False)
        self.update_account_fields()

    def update_account_fields(self):
        use_existing = self.use_existing_checkbox.isChecked()
        create_new = self.create_account_checkbox.isChecked()

        self.user_label.setVisible(use_existing)
        self.user_combo.setVisible(use_existing)
        self.username_label.setVisible(create_new)
        self.username_edit.setVisible(create_new)
        self.password_label.setVisible(create_new)
        self.password_edit.setVisible(create_new)
        self.gen_password_btn.setVisible(create_new)
        self.show_password_btn.setVisible(create_new)
        self.role_label.setVisible(create_new)
        self.role_combo.setVisible(create_new)

    def toggle_password_visibility(self):
        if self.show_password_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("❌")
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁")

    def open_password_generator(self):
        dlg = PasswordGeneratorDialog(min_length=8, parent=self)
        dlg.password_generated.connect(self.password_edit.setText)
        dlg.exec()

    def load_roles(self):
        self.role_combo.clear()
        if self.current_user.role.role_name == "superadmin":
            roles = UserRole.select()
        else:
            roles = UserRole.select().where(UserRole.role_name.not_in(["superadmin", "admin", "owner"]))
        self.role_combo.addItems([r.role_name for r in roles])
        self.allowed_roles = list(roles)

    def add_employee(self):
        try:
            full_name = self.name_edit.text().strip()
            phone = self.phone_edit.text().strip()
            email = self.email_edit.text().strip()
            hire_date = self.hire_date_edit.date().toPyDate()
            position = self.positions[self.position_combo.currentIndex()]

            position_index = self.position_combo.currentIndex()
            if position_index == 0:
                QMessageBox.warning(self, "Помилка", "Оберіть посаду для працівника.")
                return
            position = self.positions[position_index - 1]

            if not validate_full_name(full_name, parent=self): return
            if not validate_phone(phone, parent=self): return
            if not validate_email(email, parent=self): return
            if not validate_hire_date(hire_date, parent=self): return

            if Employee.select().where(Employee.email == email).exists():
                QMessageBox.warning(self, "Помилка", "Такий email вже існує.")
                return
            if Employee.select().where(Employee.phone == phone).exists():
                QMessageBox.warning(self, "Помилка", "Такий телефон вже існує.")
                return

            user = None
            if self.create_account_checkbox.isChecked():
                username = self.username_edit.text().strip()
                password = self.password_edit.text().strip()
                role_name = self.role_combo.currentText()

                if not validate_username(username, parent=self): return
                if not validate_password(password, parent=self): return
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

            new_emp = Employee.create(
                full_name=full_name,
                phone=phone,
                email=email,
                hire_date=hire_date,
                position=position,
                is_active=True,
                user=user
            )

            if position.name.lower() in ["механік", "майстер"]:
                specialization = self.specialization_combo.currentText()
                max_hours_str = self.max_hours_edit.text().strip()

                if not validate_specialization(specialization, parent=self):
                    return

                if not validate_max_hours(max_hours_str, parent=self):
                    return

                max_hours = float(max_hours_str)
                qualification = self.qualification_input.value()

                OptimizationWorker.create(
                    employee=new_emp,
                    specialization=specialization,
                    max_hours=max_hours,
                    qualification=qualification,
                    workload=0.0
                )

            QMessageBox.information(self, "Успіх", "Працівника додано.")
            self.accept()

        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося додати працівника: {ex}")

    def validate_phone_field(self):
        phone = self.phone_edit.text().strip()
        validate_phone(phone, parent=self)
