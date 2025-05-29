from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from models.user import User
from models.role import UserRole
from logic.password_service import hash_password  # Функція для хешування пароля
from logic.validators import validate_username, validate_password


class AddUserDialog(QDialog):
    """
    Діалог для додавання нового користувача.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати користувача")
        self.setFixedSize(360, 280)

        layout = QVBoxLayout()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_combo = QComboBox()
        self.roles = list(UserRole.select())
        # Исключаем superadmin для всех случаев
        self.roles = [role for role in self.roles if role.role_name != "superadmin"]
        # Если не супер-админ — исключаем admin
        if current_user.role.role_name != "superadmin":
            self.roles = [role for role in self.roles if role.role_name != "admin"]
        self.role_combo.addItems([role.role_name for role in self.roles])

        layout.addWidget(QLabel("Логін:"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_edit)
        layout.addWidget(QLabel("Роль:"))
        layout.addWidget(self.role_combo)

        self.add_btn = QPushButton("Додати")
        self.add_btn.clicked.connect(self.add_user)
        layout.addWidget(self.add_btn)
        self.setLayout(layout)


    def add_user(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        role_index = self.role_combo.currentIndex()

        # Додаткова валідація логіна
        if not validate_username(username, parent=self):
            return

        # Додаткова валідація паролю
        if not validate_password(password, parent=self):
            return

        try:
            user = User.create(
                username=username,
                password_hash=hash_password(password),
                role=self.roles[role_index],  # ForeignKey
                is_active=True
            )
            QMessageBox.information(self, "Успіх", f"Користувача '{username}' додано.")
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити користувача: {ex}")
