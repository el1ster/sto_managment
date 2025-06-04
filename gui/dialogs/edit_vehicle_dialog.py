from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QPushButton, QMessageBox
)
from models.vehicle import Vehicle
from logic.validators import (
    validate_vehicle_number,
    validate_vehicle_brand,
    validate_vehicle_model
)


class EditVehicleDialog(QDialog):
    """
    Діалог редагування транспортного засобу.

    Args:
        vehicle (Vehicle): Об’єкт транспорту для редагування.
        current_user: Поточний користувач.
        parent: Батьківський віджет.
    """

    def __init__(self, vehicle: Vehicle, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редагувати транспортний засіб")
        self.setMinimumSize(400, 400)
        self.vehicle = vehicle
        self.current_user = current_user

        layout = QVBoxLayout()

        # --- Поля ---
        self.number_input = QLineEdit(vehicle.number_plate)
        self._add_row(layout, "Номер:", self.number_input)

        self.brand_input = QLineEdit(vehicle.brand)
        self._add_row(layout, "Марка:", self.brand_input)

        self.model_input = QLineEdit(vehicle.model)
        self._add_row(layout, "Модель:", self.model_input)

        self.year_input = QSpinBox()
        self.year_input.setRange(1950, 2100)
        self.year_input.setValue(vehicle.year or 2000)
        self._add_row(layout, "Рік випуску:", self.year_input)

        self.vin_input = QLineEdit(vehicle.vin or "")
        self._add_row(layout, "VIN:", self.vin_input)

        self.type_input = QLineEdit(vehicle.vehicle_type or "")
        self._add_row(layout, "Тип:", self.type_input)

        self.department_input = QLineEdit(vehicle.department or "")
        self._add_row(layout, "Підрозділ:", self.department_input)

        self.mileage_input = QSpinBox()
        self.mileage_input.setRange(0, 1_000_000)
        self.mileage_input.setValue(vehicle.mileage or 0)
        self._add_row(layout, "Пробіг:", self.mileage_input)

        # --- Кнопки ---
        btns = QHBoxLayout()
        save_btn = QPushButton("Зберегти зміни")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)

        layout.addLayout(btns)
        self.setLayout(layout)

    def _add_row(self, layout: QVBoxLayout, label: str, widget) -> None:
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(widget)
        layout.addLayout(row)

    def save_changes(self):
        """
        Зберігає оновлені дані про транспорт.
        """
        try:
            number = self.number_input.text().strip()
            brand = self.brand_input.text().strip()
            model = self.model_input.text().strip()

            if not validate_vehicle_number(number, parent=self):
                return
            if not validate_vehicle_brand(brand, parent=self):
                return
            if not validate_vehicle_model(model, parent=self): return

            self.vehicle.number_plate = number
            self.vehicle.brand = brand
            self.vehicle.model = model
            self.vehicle.year = self.year_input.value()
            self.vehicle.vin = self.vin_input.text().strip() or None
            self.vehicle.vehicle_type = self.type_input.text().strip() or None
            self.vehicle.department = self.department_input.text().strip() or None
            self.vehicle.mileage = self.mileage_input.value()
            self.vehicle.save()

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти зміни:\n{e}")
