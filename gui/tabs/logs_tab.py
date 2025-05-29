from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal

class LogsLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    def run(self):
        try:
            # logs = list(Log.select())
            logs = [{"datetime": "2024-05-27 16:00", "action": "Увійшов superadmin"}]  # тестова заглушка
            self.data_loaded.emit(logs)
        except Exception:
            self.data_loaded.emit([])

class LogsTab(QWidget):
    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити логи")
        self.refresh_button.clicked.connect(self.load_logs)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_logs()

    def load_logs(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = LogsLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_logs_loaded)
        self.loader_thread.start()

    def on_logs_loaded(self, logs):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not logs:
            self.list_widget.addItem("Журнал подій порожній або сталася помилка")
            return
        for record in logs:
            self.list_widget.addItem(f"{record.get('datetime', '')} | {record.get('action', '')}")
