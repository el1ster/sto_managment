from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QCheckBox, QHBoxLayout
)
from models.user import User
from models.role import UserRole
from logic.password_service import hash_password
from logic.validators import validate_username, validate_password
from gui.dialogs.password_generator_dialog import PasswordGeneratorDialog


class EditUserDialog(QDialog):
    """
    Діалог для редагування існуючого користувача.
    """

    @staticmethod
    def allowed_to_edit(user, current_user):
        """
        Перевірка права на редагування користувача.
        """
        if user.role.role_name == "superadmin" and user.id != current_user.id:
            return False, "Редагування чужого супер-адміну заборонено!"
        if user.role.role_name == "admin" and current_user.role.role_name != "superadmin":
            return False, "Редагування адміністратора дозволено лише супер-адміну!"
        return True, ""

    def __init__(self, user: User, current_user, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle(f"Редагувати користувача: {user.username}")
            self.setFixedSize(360, 360)
            self.user = user
            self.current_user = current_user

            layout = QVBoxLayout()

            self.username_edit = QLineEdit(user.username)

            password_layout = QHBoxLayout()
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_edit.setPlaceholderText("Залиште порожнім, щоб не змінювати")

            self.show_pass_btn = QPushButton("👁")
            self.show_pass_btn.setCheckable(True)
            self.show_pass_btn.setFixedWidth(32)
            self.show_pass_btn.clicked.connect(self.toggle_password_visibility)

            self.gen_pass_btn = QPushButton("🔧")
            self.gen_pass_btn.setToolTip("Згенерувати новий пароль")
            self.gen_pass_btn.setFixedWidth(32)
            self.gen_pass_btn.clicked.connect(self.open_password_generator)

            password_layout.addWidget(self.password_edit)
            password_layout.addWidget(self.show_pass_btn)
            password_layout.addWidget(self.gen_pass_btn)

            self.role_combo = QComboBox()
            try:
                self.roles = [
                    role for role in UserRole.select()
                    if role.role_name != "superadmin" or user.role.role_name == "superadmin"
                ]
                self.role_combo.addItems([r.role_name for r in self.roles])
                current_index = next((i for i, r in enumerate(self.roles) if r.id == user.role.id), 0)
                self.role_combo.setCurrentIndex(current_index)
            except Exception:
                self.roles = []
                QMessageBox.critical(self, "Помилка", "Не вдалося завантажити ролі користувачів.")

            self.active_checkbox = QCheckBox("Активний")
            self.active_checkbox.setChecked(user.is_active)

            layout.addWidget(QLabel("Логін:"))
            layout.addWidget(self.username_edit)

            layout.addWidget(QLabel("Новий пароль (опційно):"))
            layout.addLayout(password_layout)

            layout.addWidget(QLabel("Роль:"))
            layout.addWidget(self.role_combo)

            layout.addWidget(self.active_checkbox)

            self.save_btn = QPushButton("Зберегти зміни")
            self.save_btn.clicked.connect(self.save_user)
            layout.addWidget(self.save_btn)

            self.setLayout(layout)

        except Exception as e:
            QMessageBox.critical(None, "Помилка", f"Не вдалося ініціалізувати вікно редагування: {e}")

    def toggle_password_visibility(self):
        """
        Перемикає видимість поля пароля.
        """
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
        """
        Відкриває генератор паролів.
        """
        try:
            dlg = PasswordGeneratorDialog(min_length=8, parent=self)
            dlg.password_generated.connect(self.password_edit.setText)
            dlg.exec()
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося відкрити генератор паролів.")

    def save_user(self):
        """
        Зберігає оновлені дані користувача.
        """
        try:
            if not self.roles:
                QMessageBox.warning(self, "Помилка", "Немає доступних ролей для збереження.")
                return

            role = self.roles[self.role_combo.currentIndex()]
            is_active = self.active_checkbox.isChecked()
            new_username = self.username_edit.text().strip()
            new_password = self.password_edit.text().strip()

            if not validate_username(new_username, parent=self):
                return

            if User.select().where((User.username == new_username) & (User.id != self.user.id)).exists():
                QMessageBox.warning(self, "Помилка", "Користувач із таким логіном вже існує.")
                return

            self.user.username = new_username
            self.user.role = role
            self.user.is_active = is_active

            if new_password:
                if not validate_password(new_password, parent=self):
                    return
                self.user.password_hash = hash_password(new_password)

            self.user.save()
            QMessageBox.information(self, "Успіх", "Дані користувача оновлено.")
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити користувача: {ex}")
