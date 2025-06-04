from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QDoubleSpinBox, QTextEdit, QPushButton, QMessageBox
)
from datetime import date
from models.maintenance_record import MaintenanceRecord
from models.vehicle import Vehicle
from models.tax_group import TaxGroup


class EditMaintenanceDialog(QDialog):
    """
    Діалогове вікно для редагування запису обслуговування транспорту.

    Args:
        record (MaintenanceRecord): Запис, який редагується.
        parent: Батьківське вікно.
    """

    def __init__(self, record: MaintenanceRecord, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редагувати запис обслуговування")
        self.setMinimumSize(420, 360)
        self.record = record

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # --- Пошук транспорту ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук транспорту...")
        self.search_edit.textChanged.connect(self.filter_vehicles)
        form.addRow("Пошук:", self.search_edit)

        self.vehicle_combo = QComboBox()
        self.vehicles = list(Vehicle.select())
        self.filtered_vehicles = self.vehicles.copy()
        self.update_vehicle_combo()
        form.addRow("Транспорт:", self.vehicle_combo)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(record.service_date or date.today())
        self.date_edit.setCalendarPopup(True)
        form.addRow("Дата обслуговування:", self.date_edit)

        self.type_input = QLineEdit(record.service_type or "")
        form.addRow("Тип обслуговування:", self.type_input)

        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 1_000_000)
        self.cost_spin.setSuffix(" грн")
        self.cost_spin.setValue(record.material_cost or 0.0)
        form.addRow("Сума:", self.cost_spin)

        self.tax_group_combo = QComboBox()
        self.tax_groups = list(TaxGroup.select())
        self.tax_group_combo.addItem("Без групи")
        self.tax_group_combo.addItems([g.group_name for g in self.tax_groups])
        selected_index = 0
        if record.tax_group:
            for i, group in enumerate(self.tax_groups):
                if group.group_id == record.tax_group.group_id:
                    selected_index = i + 1
                    break
        self.tax_group_combo.setCurrentIndex(selected_index)

        form.addRow("Група податків:", self.tax_group_combo)

        self.comment_edit = QTextEdit(record.service_desc or "")
        form.addRow("Коментар:", self.comment_edit)

        layout.addLayout(form)

        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        # Проставити вибраний транспорт у комбобокс
        self.select_vehicle_in_combo()

    def update_vehicle_combo(self):
        self.vehicle_combo.clear()
        self.vehicle_combo.addItems([v.number_plate for v in self.filtered_vehicles])

    def filter_vehicles(self, text: str):
        text = text.strip().lower()
        self.filtered_vehicles = [
            v for v in self.vehicles if text in v.number_plate.lower()
        ]
        self.update_vehicle_combo()
        self.select_vehicle_in_combo()

    def select_vehicle_in_combo(self):
        """Позначити транспорт, що відповідає record.vehicle"""
        for i, v in enumerate(self.filtered_vehicles):
            if v.id == self.record.vehicle.id:
                self.vehicle_combo.setCurrentIndex(i)
                return

    def save(self):
        try:
            if not self.filtered_vehicles:
                QMessageBox.warning(self, "Помилка", "Транспорт не обрано.")
                return

            vehicle = self.filtered_vehicles[self.vehicle_combo.currentIndex()]
            tax_group = (
                None if self.tax_group_combo.currentIndex() == 0
                else self.tax_groups[self.tax_group_combo.currentIndex() - 1]
            )

            self.record.vehicle = vehicle
            self.record.service_date = self.date_edit.date().toPyDate()
            self.record.service_type = self.type_input.text().strip()
            self.record.material_cost = self.cost_spin.value()
            self.record.tax_group = tax_group
            self.record.service_desc = self.comment_edit.toPlainText()
            self.record.save()

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти зміни: {e}")
