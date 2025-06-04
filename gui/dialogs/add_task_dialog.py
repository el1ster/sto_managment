from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QComboBox, QPushButton, QMessageBox
)
from models.task import Task
from models.vehicle import Vehicle
from models.maintenance_record import MaintenanceRecord
import config


class AddTaskDialog(QDialog):
    """
    Діалогове вікно для створення нового завдання.

    Args:
        current_user: Поточний користувач.
        parent: Батьківський віджет.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати нове завдання")
        self.setMinimumSize(500, 350)
        self.current_user = current_user

        layout = QVBoxLayout()

        # Назва
        self.name_input = QLineEdit()
        self._add_row(layout, "Назва:", self.name_input)

        # Тривалість
        self.time_input = QDoubleSpinBox()
        self.time_input.setRange(0.1, 100.0)
        self.time_input.setSuffix(" год")
        self.time_input.setSingleStep(0.25)
        self._add_row(layout, "Тривалість:", self.time_input)

        # Статус (фіксований список)
        self.status_input = QComboBox()
        self.status_input.addItems(config.TASK_STATUSES)
        self.status_input.setCurrentText("new")
        self._add_row(layout, "Статус:", self.status_input)

        # Спеціалізація (фіксований список)
        self.specialization_input = QComboBox()
        self.specialization_input.addItems(config.SPECIALIZATIONS)
        self.specialization_input.setCurrentIndex(0)
        self._add_row(layout, "Спеціалізація:", self.specialization_input)

        # Транспорт
        self.vehicle_input = QComboBox()
        self.vehicles_map = {
            f"{v.brand} {v.model} ({v.number_plate})": v for v in Vehicle.select()
        }
        self.vehicle_input.addItems(self.vehicles_map.keys())
        self._add_row(layout, "Автомобіль:", self.vehicle_input)

        # Обслуговування
        self.maintenance_input = QComboBox()
        self.maintenance_map = {
            f"{r.service_date} - {r.service_type}": r for r in MaintenanceRecord.select()
        }
        self.maintenance_input.addItems(self.maintenance_map.keys())
        self._add_row(layout, "Обслуговування:", self.maintenance_input)

        # Кнопки
        btns = QHBoxLayout()
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_task)
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

    def save_task(self) -> None:
        """
        Зберігає нову задачу в базу даних.
        """
        try:
            name = self.name_input.text().strip()
            time = self.time_input.value()
            status = self.status_input.currentText()
            specialization = self.specialization_input.currentText()

            if not name or not specialization:
                QMessageBox.warning(self, "Помилка", "Заповніть усі обов’язкові поля.")
                return

            vehicle = self.vehicles_map[self.vehicle_input.currentText()]
            maintenance = self.maintenance_map[self.maintenance_input.currentText()]

            Task.create(
                name=name,
                time_required=time,
                status=status,
                specialization=specialization,
                vehicle=vehicle,
                maintenance=maintenance,
                is_archived=(status == "completed")
            )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти задачу:\n{e}")
