from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal
from models.user import User

class UsersLoaderThread(QThread):
    data_loaded = pyqtSignal(list)

    def run(self):
        try:
            users = list(User.select())
            self.data_loaded.emit(users)
        except Exception:
            self.data_loaded.emit([])

class UsersTab(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити список користувачів")
        self.refresh_button.clicked.connect(self.load_users)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_users()

    def load_users(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = UsersLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_users_loaded)
        self.loader_thread.start()

    def on_users_loaded(self, users):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not users:
            self.list_widget.addItem("Немає користувачів або сталася помилка")
            return
        for user in users:
            self.list_widget.addItem(f"{user.username} | роль: {user.role_id}")
