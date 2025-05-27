from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal

class VehiclesLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    def run(self):
        try:
            # vehicles = list(Vehicle.select())
            vehicles = [{"number_plate": "AA1234AA", "brand": "Toyota"}]  # тестова заглушка
            self.data_loaded.emit(vehicles)
        except Exception:
            self.data_loaded.emit([])

class VehiclesTab(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити транспорт")
        self.refresh_button.clicked.connect(self.load_vehicles)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_vehicles()

    def load_vehicles(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = VehiclesLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_vehicles_loaded)
        self.loader_thread.start()

    def on_vehicles_loaded(self, vehicles):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not vehicles:
            self.list_widget.addItem("Немає транспорту або сталася помилка")
            return
        for car in vehicles:
            self.list_widget.addItem(f"{car.get('number_plate', '')} | {car.get('brand', '')}")
