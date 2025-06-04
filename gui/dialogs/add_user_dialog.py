from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QHBoxLayout
)
from models.user import User
from models.role import UserRole
from logic.password_service import hash_password
from logic.validators import validate_username, validate_password
from gui.dialogs.password_generator_dialog import PasswordGeneratorDialog
from peewee import IntegrityError


class AddUserDialog(QDialog):
    """
    Діалог для додавання нового користувача.
    """

    def __init__(self, current_user, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle("Додати користувача")
            self.setFixedSize(360, 320)
            self.current_user = current_user

            layout = QVBoxLayout()
            self.username_edit = QLineEdit()

            # --- Поле паролю + кнопки управління ---
            password_layout = QHBoxLayout()
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

            self.show_pass_btn = QPushButton("👁")
            self.show_pass_btn.setCheckable(True)
            self.show_pass_btn.setFixedWidth(32)
            self.show_pass_btn.clicked.connect(self.toggle_password_visibility)

            self.gen_password_btn = QPushButton("🔧")
            self.gen_password_btn.setToolTip("Згенерувати пароль")
            self.gen_password_btn.setFixedWidth(32)
            self.gen_password_btn.clicked.connect(self.open_password_generator)

            password_layout.addWidget(self.password_edit)
            password_layout.addWidget(self.show_pass_btn)
            password_layout.addWidget(self.gen_password_btn)

            # --- Ролі ---
            self.role_combo = QComboBox()

            try:
                self.roles = list(UserRole.select())
                self.roles = [r for r in self.roles if r.role_name != "superadmin"]
                if self.current_user.role.role_name != "superadmin":
                    self.roles = [r for r in self.roles if r.role_name != "admin"]
                self.role_combo.addItems([r.role_name for r in self.roles])
            except Exception:
                self.roles = []
                QMessageBox.critical(self, "Помилка", "Не вдалося завантажити ролі користувачів.")

            # --- Побудова макету ---
            try:
                layout.addWidget(QLabel("Логін:"))
                layout.addWidget(self.username_edit)

                layout.addWidget(QLabel("Пароль:"))
                layout.addLayout(password_layout)

                layout.addWidget(QLabel("Роль:"))
                layout.addWidget(self.role_combo)

                self.add_btn = QPushButton("Додати")
                self.add_btn.clicked.connect(self.add_user)
                layout.addWidget(self.add_btn)

                self.setLayout(layout)
            except Exception:
                QMessageBox.critical(self, "Помилка", "Помилка при створенні макету інтерфейсу.")
        except Exception as e:
            QMessageBox.critical(None, "Критична помилка", f"Не вдалося ініціалізувати діалог: {e}")

    def toggle_password_visibility(self):
        """
        Перемикає видимість пароля.
        """
        try:
            if self.show_pass_btn.isChecked():
                self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
                self.show_pass_btn.setText("❌")
            else:
                self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
                self.show_pass_btn.setText("👁")
        except Exception:
            QMessageBox.warning(self, "Помилка", "Не вдалося перемкнути режим відображення пароля.")

    def open_password_generator(self):
        """
        Відкриває діалог генератора пароля.
        """
        try:
            dlg = PasswordGeneratorDialog(min_length=8, parent=self)
            dlg.password_generated.connect(self.password_edit.setText)
            dlg.exec()
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося відкрити генератор паролів.")

    def add_user(self):
        """
        Створює нового користувача після валідації.
        """
        try:
            username = self.username_edit.text().strip()
            password = self.password_edit.text()
            role_index = self.role_combo.currentIndex()

            if not validate_username(username, parent=self):
                return
            if not validate_password(password, parent=self):
                return

            try:
                user = User.create(
                    username=username,
                    password_hash=hash_password(password),
                    role=self.roles[role_index],
                    is_active=True
                )
                QMessageBox.information(self, "Успіх", f"Користувача '{username}' додано.")
                self.accept()
            except (IntegrityError, IndexError) as ex:
                QMessageBox.critical(self, "Помилка", f"Не вдалося створити користувача: {ex}")
        except Exception as ex:
            QMessageBox.critical(self, "Критична помилка", f"Помилка при обробці введення: {ex}")
