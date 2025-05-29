from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from logic.auth_service import reset_user_password, authenticate_user
from models.user import User
from logic.validators import validate_password


class ResetPasswordDialog(QDialog):
    """
    Діалогове вікно для скидання пароля користувача.
    """

    def __init__(self, username, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Скидання пароля")
        self.setFixedSize(350, 220)

        self.username = username
        self.current_user = current_user

        layout = QVBoxLayout()
        self.info_label = QLabel(f"Скидання пароля для користувача: {username}")
        self.new_password_label = QLabel("Новий пароль:")
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.superadmin_pass_label = QLabel("Пароль SuperAdmin:")
        self.superadmin_pass_edit = QLineEdit()
        self.superadmin_pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.superadmin_pass_label.hide()
        self.superadmin_pass_edit.hide()

        self.reset_btn = QPushButton("Скинути")
        self.reset_btn.clicked.connect(self.reset_password)

        layout.addWidget(self.info_label)
        layout.addWidget(self.new_password_label)
        layout.addWidget(self.new_password_edit)
        layout.addWidget(self.superadmin_pass_label)
        layout.addWidget(self.superadmin_pass_edit)
        layout.addWidget(self.reset_btn)
        self.setLayout(layout)

        # Перевіряємо роль та кого скидаємо — показуємо поле для пароля SuperAdmin, якщо треба
        user_to_reset = User.get_or_none(User.username == username)
        if user_to_reset and user_to_reset.role_id == 1:
            self.superadmin_pass_label.show()
            self.superadmin_pass_edit.show()

    def reset_password(self):
        new_password = self.new_password_edit.text().strip()
        user = User.get_or_none(User.username == self.username)
        if not user:
            QMessageBox.warning(self, "Помилка", "Користувача не знайдено.")
            return
        print(user.role_id)
        # 1. Скидання пароля SuperAdmin — перевіряємо пароль суперкористувача
        if user.role_id == 1:
            superadmin_pass = self.superadmin_pass_edit.text().strip()
            # Дозволяємо скидання лише якщо current_user сам SuperAdmin, або при запуску з LoginDialog (current_user=None)
            if self.current_user is not None and self.current_user.role_id != 1:
                QMessageBox.warning(self, "Помилка", "Лише SuperAdmin може скинути пароль SuperAdmin.")
                return
            if not authenticate_user('superadmin', superadmin_pass):
                QMessageBox.warning(self, "Помилка", "Невірний пароль SuperAdmin!")
                return

        # 2. Скидання пароля адміну — тільки SuperAdmin
        if user.role_id == 2:
            if self.current_user is None or self.current_user.role_id != 1:
                QMessageBox.warning(self, "Помилка", "Тільки SuperAdmin може скинути пароль адміністратору.")
                return

        if not validate_password(new_password, parent=self):
            return

        if reset_user_password(user.id, new_password):
            QMessageBox.information(self, "Успіх", "Пароль успішно скинуто.")
            self.accept()
        else:
            QMessageBox.warning(self, "Помилка", "Не вдалося скинути пароль.")
