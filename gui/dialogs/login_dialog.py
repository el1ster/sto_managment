from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import logic.auth_service as auth_service


class AuthThread(QThread):
    auth_result = pyqtSignal(object)  # object: або user, або None

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        user = auth_service.authenticate_user(self.username, self.password)
        self.auth_result.emit(user)


class LoginDialog(QDialog):
    """
    Діалогове вікно для входу користувача.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вхід до системи")
        self.setFixedSize(320, 180)

        layout = QVBoxLayout()
        self.login_label = QLabel("Логін:")
        self.login_edit = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Увійти")
        self.login_button.clicked.connect(self.try_login)

        layout.addWidget(self.login_label)
        layout.addWidget(self.login_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.auth_thread = None
        self.user = None

    def try_login(self):
        username = self.login_edit.text().strip()
        password = self.password_edit.text()
        self.login_button.setEnabled(False)

        self.auth_thread = AuthThread(username, password)
        self.auth_thread.auth_result.connect(self.on_auth_result)
        self.auth_thread.start()

    def on_auth_result(self, user):
        self.login_button.setEnabled(True)
        if user:
            self.user = user
            print(user)
            self.accept()  # закриває діалог з успіхом
        else:
            QMessageBox.warning(self, "Помилка", "Невірний логін або пароль!")
