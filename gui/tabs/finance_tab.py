from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal

class FinanceLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    def run(self):
        try:
            # data = list(Finance.select())  # твоя модель
            data = [{"category": "Зарплата", "amount": "10000 UAH"}]  # тестова заглушка
            self.data_loaded.emit(data)
        except Exception:
            self.data_loaded.emit([])

class FinanceTab(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити фінанси")
        self.refresh_button.clicked.connect(self.load_finance)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_finance()

    def load_finance(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = FinanceLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_finance_loaded)
        self.loader_thread.start()

    def on_finance_loaded(self, data):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not data:
            self.list_widget.addItem("Даних немає або сталася помилка")
            return
        for record in data:
            self.list_widget.addItem(f"{record.get('category', '')}: {record.get('amount', '')}")
