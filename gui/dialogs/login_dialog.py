from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout, QWidget, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import logic.auth_service as auth_service
from logic.user_settings_service import get_setting, set_setting


class AuthThread(QThread):
    auth_result = pyqtSignal(object)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        user = auth_service.authenticate_user(self.username, self.password)
        self.auth_result.emit(user)


class LoginDialog(QDialog):
    """
    Діалогове вікно для входу користувача з можливістю скидання пароля.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вхід до системи")
        self.setFixedSize(420, 200)

        layout = QVBoxLayout()
        self.login_label = QLabel("Логін:")
        self.login_edit = QLineEdit()
        self.password_label = QLabel("Пароль:")

        # --- Поле пароля и кнопки управления ---
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setText("SuperPass1!")

        # Кнопка показать/скрыть пароль
        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.setFixedWidth(32)
        self.show_pass_btn.clicked.connect(self.toggle_password_visibility)

        # Кнопка вставить пароль из буфера
        self.paste_pass_btn = QPushButton("📋")
        self.paste_pass_btn.setFixedWidth(32)
        self.paste_pass_btn.clicked.connect(self.paste_password_from_clipboard)

        # Layout для поля пароля и двух кнопок справа
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.password_edit)
        pass_layout.addWidget(self.show_pass_btn)
        pass_layout.addWidget(self.paste_pass_btn)

        # --- Кнопки управления входом ---
        self.login_button = QPushButton("Увійти")
        self.login_button.clicked.connect(self.try_login)

        self.reset_pass_button = QPushButton("Скинути пароль")
        self.reset_pass_button.clicked.connect(self.open_reset_password_dialog)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.login_button)
        btn_layout.addWidget(self.reset_pass_button)

        # --- Добавляем всё в основной layout ---
        layout.addWidget(self.login_label)
        layout.addWidget(self.login_edit)
        layout.addWidget(self.password_label)
        layout.addLayout(pass_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.auth_thread = None
        self.user = None
        last_login = get_setting("last_login", "")
        if last_login:
            self.login_edit.setText(last_login)

    def toggle_password_visibility(self):
        if self.show_pass_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pass_btn.setText("❌")  # Или любой другой значок
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pass_btn.setText("👁")

    def paste_password_from_clipboard(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            text = clipboard.text()
            self.password_edit.setText(text)

    def try_login(self):
        username = self.login_edit.text().strip()
        set_setting("last_login", username)
        password = self.password_edit.text()
        self.login_button.setEnabled(False)

        self.auth_thread = AuthThread(username, password)
        self.auth_thread.auth_result.connect(self.on_auth_result)
        self.auth_thread.start()

    def on_auth_result(self, user):
        self.login_button.setEnabled(True)
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Помилка", "Невірний логін або пароль!")

    def open_reset_password_dialog(self):
        print("DEBUG: Open reset password dialog called")
        login = self.login_edit.text().strip()
        if not login:
            QMessageBox.warning(self, "Помилка", "Введіть логін для скидання пароля!")
            return

        from models.user import User
        user = User.get_or_none(User.username == login)
        if not user:
            QMessageBox.warning(self, "Помилка", "Користувача не знайдено.")
            return

        # Скидання пароля для адміністраторів — тільки через superadmin
        if user.role_id in [1, 2]:
            from gui.dialogs.admin_confirm_dialog import AdminConfirmDialog
            confirm_dialog = AdminConfirmDialog(self)
            if confirm_dialog.exec():
                admin_user = confirm_dialog.admin_user
                if admin_user.role_id != 1:
                    QMessageBox.warning(self, "Помилка", "Скинути пароль адміністратору може тільки супер-адмін.")
                    return
                from gui.dialogs.reset_password_dialog import ResetPasswordDialog
                dlg = ResetPasswordDialog(login, admin_user, self)
                dlg.exec()
            return

        # Для інших користувачів — підтвердження адміністратором або супер-адміном
        from gui.dialogs.admin_confirm_dialog import AdminConfirmDialog
        confirm_dialog = AdminConfirmDialog(self)
        if confirm_dialog.exec():
            admin_user = confirm_dialog.admin_user
            from gui.dialogs.reset_password_dialog import ResetPasswordDialog
            dlg = ResetPasswordDialog(login, admin_user, self)
            dlg.exec()
