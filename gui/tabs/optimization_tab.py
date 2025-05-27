from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal

class OptimizationLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    def run(self):
        try:
            # optim_data = list(Optimization.select())
            optim_data = [{"worker": "Petrenko", "load": "80%"}]  # тестова заглушка
            self.data_loaded.emit(optim_data)
        except Exception:
            self.data_loaded.emit([])

class OptimizationTab(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити оптимізацію")
        self.refresh_button.clicked.connect(self.load_optimization)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_optimization()

    def load_optimization(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = OptimizationLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_optimization_loaded)
        self.loader_thread.start()

    def on_optimization_loaded(self, data):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not data:
            self.list_widget.addItem("Даних по оптимізації немає або сталася помилка")
            return
        for record in data:
            self.list_widget.addItem(f"{record.get('worker', '')} | Навантаження: {record.get('load', '')}")
