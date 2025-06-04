from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QPushButton, QMessageBox
)
from models.vehicle import Vehicle


class AddVehicleDialog(QDialog):
    """
    Діалогове вікно для додавання нового транспортного засобу.

    Args:
        current_user: Поточний користувач.
        parent: Батьківський віджет.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати транспортний засіб")
        self.setMinimumSize(400, 400)
        self.current_user = current_user

        layout = QVBoxLayout()

        # --- Поля вводу ---
        self.number_input = QLineEdit()
        self._add_row(layout, "Номер:", self.number_input)

        self.brand_input = QLineEdit()
        self._add_row(layout, "Марка:", self.brand_input)

        self.model_input = QLineEdit()
        self._add_row(layout, "Модель:", self.model_input)

        self.year_input = QSpinBox()
        self.year_input.setRange(1950, 2100)
        self._add_row(layout, "Рік випуску:", self.year_input)

        self.vin_input = QLineEdit()
        self._add_row(layout, "VIN:", self.vin_input)

        self.type_input = QLineEdit()
        self._add_row(layout, "Тип:", self.type_input)

        self.department_input = QLineEdit()
        self._add_row(layout, "Підрозділ:", self.department_input)

        self.mileage_input = QSpinBox()
        self.mileage_input.setRange(0, 1_000_000)
        self._add_row(layout, "Пробіг:", self.mileage_input)

        # --- Кнопки ---
        btns = QHBoxLayout()
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_vehicle)
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

    def save_vehicle(self):
        """
        Зберігає новий транспорт у БД після перевірки.
        """
        try:
            number = self.number_input.text().strip()
            brand = self.brand_input.text().strip()
            model = self.model_input.text().strip()

            if not validate_vehicle_number(number, parent=self):
                return
            if not validate_vehicle_brand(brand, parent=self):
                return
            if not validate_vehicle_model(model, parent=self):
                return

            vehicle = Vehicle.create(
                number_plate=number,
                brand=brand,
                model=model,
                year=self.year_input.value(),
                vin=self.vin_input.text().strip() or None,
                vehicle_type=self.type_input.text().strip() or None,
                department=self.department_input.text().strip() or None,
                mileage=self.mileage_input.value()
            )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти транспорт:\n{e}")
