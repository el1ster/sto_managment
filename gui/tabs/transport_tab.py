from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QHeaderView
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from models.vehicle import Vehicle
from gui.dialogs.add_vehicle_dialog import AddVehicleDialog
from gui.dialogs.edit_vehicle_dialog import EditVehicleDialog
from gui.dialogs.vehicle_card_dialog import VehicleCardDialog
from models.maintenance_record import MaintenanceRecord
from models.task import Task


class VehiclesLoaderThread(QThread):
    data_loaded = pyqtSignal(list)

    def run(self):
        try:
            vehicles = list(Vehicle.select().where(Vehicle.is_archived.is_null(True)))
            self.data_loaded.emit(vehicles)
        except Exception:
            self.data_loaded.emit([])


class TransportTab(QWidget):
    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        admin_roles = ["admin", "superadmin"]
        if self.current_user.role.role_name not in admin_roles:
            layout = QVBoxLayout()
            label = QLabel("У вас немає доступу до цієї вкладки")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)
            return

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        search_layout = QHBoxLayout()

        self.add_button = QPushButton("Додати")
        self.edit_button = QPushButton("Редагувати")
        self.delete_button = QPushButton("Видалити")
        self.refresh_button = QPushButton("Оновити")

        self.add_button.clicked.connect(self.open_add_vehicle_dialog)
        self.edit_button.clicked.connect(self.open_edit_vehicle_dialog)
        self.delete_button.clicked.connect(self.delete_vehicle_dialog)
        self.refresh_button.clicked.connect(self.load_vehicles)

        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.refresh_button)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук по транспорту...")
        self.search_edit.textChanged.connect(self.apply_filter)
        search_layout.addWidget(QLabel("Пошук:"))
        search_layout.addWidget(self.search_edit)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Назва", "Номер", "Тип", "Рік", "VIN", "Пробіг (км)"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.show_vehicle_card)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)

        main_layout.addLayout(btn_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        self.all_vehicles = []
        self.load_vehicles()

    def load_vehicles(self):
        try:
            self.refresh_button.setEnabled(False)
            self.table.setRowCount(0)
            loader = VehiclesLoaderThread()
            loader.data_loaded.connect(self.on_vehicles_loaded)
            loader.start()
            self.loader_thread = loader
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося завантажити транспорт.")

    def on_vehicles_loaded(self, vehicles):
        self.refresh_button.setEnabled(True)
        self.all_vehicles = vehicles
        self.apply_filter()

    def apply_filter(self):
        try:
            query = self.search_edit.text().strip().lower()
            filtered = []
            for v in self.all_vehicles:
                search_string = " ".join([
                    f"{v.brand} {v.model}".lower(),
                    v.number_plate.lower() if v.number_plate else "",
                    v.vehicle_type.lower() if v.vehicle_type else "",
                    str(v.year) if v.year else "",
                    v.vin.lower() if v.vin else "",
                    str(v.mileage) if hasattr(v, "mileage") and v.mileage is not None else ""
                ])
                if query in search_string:
                    filtered.append(v)
            self.show_vehicles(filtered)
        except Exception:
            QMessageBox.critical(self, "Помилка", "Помилка при фільтрації транспорту.")

    def show_vehicles(self, vehicles):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(vehicles))
        for i, v in enumerate(vehicles):
            self.table.setItem(i, 0, QTableWidgetItem(f"{v.brand} {v.model}"))
            self.table.setItem(i, 1, QTableWidgetItem(v.number_plate or "-"))
            self.table.setItem(i, 2, QTableWidgetItem(v.vehicle_type or "-"))
            self.table.setItem(i, 3, QTableWidgetItem(str(v.year) if v.year else "-"))
            self.table.setItem(i, 4, QTableWidgetItem(v.vin or "-"))
            self.table.setItem(i, 5, QTableWidgetItem(str(v.mileage) if hasattr(v, "mileage") and v.mileage is not None else "-"))
        self.table.setSortingEnabled(True)

    def get_selected_vehicle(self):
        try:
            selected = self.table.selectedItems()
            if not selected:
                return None
            row = selected[0].row()
            name_displayed = self.table.item(row, 0).text()
            for v in self.all_vehicles:
                if f"{v.brand} {v.model}" == name_displayed:
                    return v
            return None
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося отримати обраний транспорт.")
            return None

    def open_add_vehicle_dialog(self):
        dlg = AddVehicleDialog(current_user=self.current_user, parent=self)
        if dlg.exec():
            self.load_vehicles()

    def open_edit_vehicle_dialog(self):
        v = self.get_selected_vehicle()
        if not v:
            QMessageBox.warning(self, "Помилка", "Оберіть транспорт для редагування.")
            return
        dlg = EditVehicleDialog(vehicle=v, current_user=self.current_user, parent=self)
        if dlg.exec():
            self.load_vehicles()

    def delete_vehicle_dialog(self):
        try:
            vehicle = self.get_selected_vehicle()
            if not vehicle:
                QMessageBox.warning(self, "Помилка", "Оберіть транспорт для видалення.")
                return

            if MaintenanceRecord.select().where(MaintenanceRecord.vehicle == vehicle).exists():
                QMessageBox.warning(
                    self, "Видалення неможливе",
                    "Неможливо видалити транспорт, оскільки існують записи обслуговування."
                )
                return

            if Task.select().where(Task.vehicle == vehicle).exists():
                QMessageBox.warning(
                    self, "Видалення неможливе",
                    "Неможливо видалити транспорт, оскільки він прив'язаний до задач."
                )
                return

            res = QMessageBox.question(
                self, "Підтвердження",
                f"Ви дійсно бажаєте видалити транспорт з номером '{vehicle.number_plate}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if res == QMessageBox.StandardButton.Yes:
                vehicle.delete_instance()
                self.load_vehicles()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при видаленні транспорту: {e}")

    def show_vehicle_card(self):
        v = self.get_selected_vehicle()
        if not v:
            return
        dlg = VehicleCardDialog(vehicle=v, parent=self)
        dlg.exec()
