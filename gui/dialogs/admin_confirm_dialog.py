from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from logic.auth_service import authenticate_user


class AdminConfirmDialog(QDialog):
    """
    Діалог підтвердження дій адміністратора.
    """

    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle("Підтвердження адміністратора")
            self.setFixedSize(320, 160)

            layout = QVBoxLayout()

            self.login_label = QLabel("Логін адміністратора:")
            self.login_edit = QLineEdit()

            self.password_label = QLabel("Пароль адміністратора:")
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

            self.confirm_btn = QPushButton("Підтвердити")
            self.confirm_btn.clicked.connect(self.check_admin)

            layout.addWidget(self.login_label)
            layout.addWidget(self.login_edit)
            layout.addWidget(self.password_label)
            layout.addWidget(self.password_edit)
            layout.addWidget(self.confirm_btn)

            self.setLayout(layout)
            self.admin_user = None  # Сюди буде збережено об'єкт User при успішній перевірці

        except Exception as e:
            QMessageBox.critical(None, "Помилка ініціалізації", f"Не вдалося створити діалог підтвердження: {e}")

    def check_admin(self):
        """
        Перевіряє логін і пароль адміністратора та підтверджує дію.
        """
        try:
            login = self.login_edit.text().strip()
            password = self.password_edit.text().strip()

            user = authenticate_user(login, password)
            if not user:
                QMessageBox.warning(self, "Помилка", "Невірний логін або пароль адміністратора!")
                return

            if user.role_id not in [1, 2]:  # 1 = superadmin, 2 = admin
                QMessageBox.warning(self, "Помилка", "Ви не адміністратор!")
                return

            self.admin_user = user
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Сталася помилка при перевірці адміністратора: {e}")
