from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from logic.auth_service import reset_user_password, authenticate_user
from models.user import User
from logic.validators import validate_password
from gui.dialogs.password_generator_dialog import PasswordGeneratorDialog


class ResetPasswordDialog(QDialog):
    """
    Діалогове вікно для скидання пароля користувача.
    """

    def __init__(self, username, current_user, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle("Скидання пароля")
            self.setFixedSize(380, 250)

            self.username = username
            self.current_user = current_user

            layout = QVBoxLayout()
            self.info_label = QLabel(f"Скидання пароля для користувача: {username}")
            self.new_password_label = QLabel("Новий пароль:")

            password_layout = QHBoxLayout()
            self.new_password_edit = QLineEdit()
            self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

            self.gen_password_btn = QPushButton("🔧")
            self.gen_password_btn.setToolTip("Згенерувати пароль")
            self.gen_password_btn.setFixedWidth(32)
            self.gen_password_btn.clicked.connect(self.open_password_generator)

            self.show_pass_btn = QPushButton("👁")
            self.show_pass_btn.setToolTip("Показати/сховати пароль")
            self.show_pass_btn.setCheckable(True)
            self.show_pass_btn.setFixedWidth(32)
            self.show_pass_btn.clicked.connect(self.toggle_password_visibility)

            password_layout.addWidget(self.new_password_edit)
            password_layout.addWidget(self.gen_password_btn)
            password_layout.addWidget(self.show_pass_btn)

            self.superadmin_pass_label = QLabel("Пароль SuperAdmin:")
            self.superadmin_pass_edit = QLineEdit()
            self.superadmin_pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.superadmin_pass_label.hide()
            self.superadmin_pass_edit.hide()

            self.reset_btn = QPushButton("Скинути")
            self.reset_btn.clicked.connect(self.reset_password)

            layout.addWidget(self.info_label)
            layout.addWidget(self.new_password_label)
            layout.addLayout(password_layout)
            layout.addWidget(self.superadmin_pass_label)
            layout.addWidget(self.superadmin_pass_edit)
            layout.addWidget(self.reset_btn)
            self.setLayout(layout)

            try:
                user_to_reset = User.get_or_none(User.username == username)
                if user_to_reset and user_to_reset.role_id == 1:
                    self.superadmin_pass_label.show()
                    self.superadmin_pass_edit.show()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося визначити роль користувача: {e}")
        except Exception as e:
            QMessageBox.critical(None, "Критична помилка", f"Не вдалося ініціалізувати діалог: {e}")

    def open_password_generator(self):
        try:
            dlg = PasswordGeneratorDialog(min_length=8, parent=self)
            dlg.password_generated.connect(self.new_password_edit.setText)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити генератор паролів: {e}")

    def toggle_password_visibility(self):
        try:
            if self.show_pass_btn.isChecked():
                self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
                self.show_pass_btn.setText("❌")
            else:
                self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
                self.show_pass_btn.setText("👁")
        except Exception:
            QMessageBox.warning(self, "Помилка", "Не вдалося змінити видимість пароля.")

    def reset_password(self):
        try:
            new_password = self.new_password_edit.text().strip()
            user = User.get_or_none(User.username == self.username)
            if not user:
                QMessageBox.warning(self, "Помилка", "Користувача не знайдено.")
                return

            if user.role_id == 1:
                superadmin_pass = self.superadmin_pass_edit.text().strip()
                if self.current_user is not None and self.current_user.role_id != 1:
                    QMessageBox.warning(self, "Помилка", "Лише SuperAdmin може скинути пароль SuperAdmin.")
                    return
                if not authenticate_user("superadmin", superadmin_pass):
                    QMessageBox.warning(self, "Помилка", "Невірний пароль SuperAdmin!")
                    return

            if user.role_id == 2 and (self.current_user is None or self.current_user.role_id != 1):
                QMessageBox.warning(self, "Помилка", "Тільки SuperAdmin може скинути пароль адміністратору.")
                return

            if not validate_password(new_password, parent=self):
                return

            if reset_user_password(user.id, new_password):
                QMessageBox.information(self, "Успіх", "Пароль успішно скинуто.")
                self.accept()
            else:
                QMessageBox.warning(self, "Помилка", "Не вдалося скинути пароль.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при скиданні пароля: {e}")
