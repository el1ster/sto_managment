from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal

class PartsLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    def run(self):
        try:
            # parts = list(Part.select())
            parts = [{"part_name": "Масляний фільтр", "qty": "12"}]  # тестова заглушка
            self.data_loaded.emit(parts)
        except Exception:
            self.data_loaded.emit([])

class PartsTab(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити запчастини")
        self.refresh_button.clicked.connect(self.load_parts)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_parts()

    def load_parts(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = PartsLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_parts_loaded)
        self.loader_thread.start()

    def on_parts_loaded(self, parts):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not parts:
            self.list_widget.addItem("Немає запчастин або сталася помилка")
            return
        for part in parts:
            self.list_widget.addItem(f"{part.get('part_name', '')} | Кількість: {part.get('qty', '')}")
