from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QComboBox, QPushButton, QMessageBox, QCheckBox
)
from models.task import Task
from models.vehicle import Vehicle
from models.maintenance_record import MaintenanceRecord
import config


class EditTaskDialog(QDialog):
    """
    Діалог редагування існуючої задачі.

    Args:
        task (Task): Об'єкт завдання для редагування.
        current_user: Поточний користувач.
        parent: Батьківський віджет.
    """

    def __init__(self, task: Task, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редагувати завдання")
        self.setMinimumSize(500, 400)
        self.task = task
        self.current_user = current_user

        layout = QVBoxLayout()

        self.name_input = QLineEdit(task.name)
        self._add_row(layout, "Назва:", self.name_input)

        self.time_input = QDoubleSpinBox()
        self.time_input.setRange(0.1, 100.0)
        self.time_input.setSuffix(" год")
        self.time_input.setSingleStep(0.25)
        self.time_input.setValue(task.time_required)
        self._add_row(layout, "Тривалість:", self.time_input)

        self.status_input = QComboBox()
        self.status_input.addItems(config.TASK_STATUSES)

        if task.status in config.TASK_STATUSES:
            self.status_input.setCurrentText(task.status)
        else:
            self.status_input.setCurrentText("new")

        self.status_input.currentTextChanged.connect(self._on_status_changed)
        self._add_row(layout, "Статус:", self.status_input)

        self.specialization_input = QComboBox()
        self.specialization_input.addItems(config.SPECIALIZATIONS)
        if task.specialization in config.SPECIALIZATIONS:
            self.specialization_input.setCurrentText(task.specialization)
        else:
            self.specialization_input.setCurrentIndex(0)
        self._add_row(layout, "Спеціалізація:", self.specialization_input)

        self.vehicle_input = QComboBox()
        self.vehicles_map = {
            f"{v.brand} {v.model} ({v.number_plate})": v for v in Vehicle.select()
        }
        self.vehicle_input.addItems(self.vehicles_map.keys())
        current_vehicle_key = next(
            (k for k, v in self.vehicles_map.items() if v.id == task.vehicle.id), None
        )
        if current_vehicle_key:
            self.vehicle_input.setCurrentText(current_vehicle_key)
        self._add_row(layout, "Автомобіль:", self.vehicle_input)

        self.maintenance_input = QComboBox()
        self.maintenance_map = {
            f"{r.service_date} - {r.service_type}": r for r in MaintenanceRecord.select()
        }
        self.maintenance_input.addItems(self.maintenance_map.keys())
        current_record_key = next(
            (k for k, r in self.maintenance_map.items() if r.id == task.maintenance.id), None
        )
        if current_record_key:
            self.maintenance_input.setCurrentText(current_record_key)
        self._add_row(layout, "Обслуговування:", self.maintenance_input)

        self.archive_checkbox = QCheckBox("Задача архівована")
        self.archive_checkbox.setChecked(task.is_archived)
        layout.addWidget(self.archive_checkbox)

        # Кнопки
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

    def _on_status_changed(self, status: str) -> None:
        """
        Автоматично вмикає архівацію при статусі completed.
        """
        if status == "completed":
            self.archive_checkbox.setChecked(True)

    def save_changes(self) -> None:
        """
        Оновлює завдання в базі.
        """
        try:
            name = self.name_input.text().strip()
            time = self.time_input.value()
            status = self.status_input.currentText()
            specialization = self.specialization_input.currentText()

            if not name or not specialization:
                QMessageBox.warning(self, "Помилка", "Заповніть усі обов’язкові поля.")
                return

            self.task.name = name
            self.task.time_required = time
            self.task.status = status
            self.task.specialization = specialization
            self.task.vehicle = self.vehicles_map[self.vehicle_input.currentText()]
            self.task.maintenance = self.maintenance_map[self.maintenance_input.currentText()]
            self.task.is_archived = self.archive_checkbox.isChecked()

            self.task.save()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти зміни:\n{e}")
