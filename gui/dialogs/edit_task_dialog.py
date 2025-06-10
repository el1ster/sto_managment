from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QComboBox, QPushButton, QMessageBox, QCheckBox
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import QDateEdit
from models.task import Task
from models.vehicle import Vehicle
from models.maintenance_record import MaintenanceRecord
from models.employee import Employee
from logic.workload_utils import recalculate_workload
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
        try:
            super().__init__(parent)
            self.setWindowTitle("Редагувати завдання")
            self.setMinimumSize(500, 400)
            self.task = task
            self.current_user = current_user

            layout = QVBoxLayout()

            # Назва
            self.name_input = QLineEdit(task.name)
            self._add_row(layout, "Назва:", self.name_input)

            # Тривалість
            self.time_input = QDoubleSpinBox()
            self.time_input.setRange(0.1, 100.0)
            self.time_input.setSuffix(" год")
            self.time_input.setSingleStep(0.25)
            self.time_input.setValue(task.time_required)
            self._add_row(layout, "Тривалість:", self.time_input)

            # Статус
            self.status_input = QComboBox()
            self.status_input.addItems(config.TASK_STATUSES)
            self.status_input.setCurrentText(task.status if task.status in config.TASK_STATUSES else "new")
            self.status_input.currentTextChanged.connect(self._on_status_changed)
            self._add_row(layout, "Статус:", self.status_input)

            # Спеціалізація
            self.specialization_input = QComboBox()
            self.specialization_input.addItems(config.SPECIALIZATIONS)
            self.specialization_input.setCurrentText(
                task.specialization if task.specialization in config.SPECIALIZATIONS else config.SPECIALIZATIONS[0])
            self._add_row(layout, "Спеціалізація:", self.specialization_input)

            # Автомобіль
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
            self.vehicle_input.currentTextChanged.connect(self.update_maintenance_list)
            self._add_row(layout, "Автомобіль:", self.vehicle_input)

            # Усі записи обслуговувань
            self.all_maintenance_records = list(MaintenanceRecord.select())

            # Обслуговування
            self.maintenance_input = QComboBox()
            self.maintenance_map = {}
            self._fill_maintenance_by_vehicle()
            self.maintenance_input.currentTextChanged.connect(self._on_maintenance_changed)
            self._add_row(layout, "Обслуговування:", self.maintenance_input)

            # Чекбокс "Призначити вручну"
            self.manual_assign_checkbox = QCheckBox("Призначити виконавця вручну")
            self.manual_assign_checkbox.stateChanged.connect(self.toggle_worker_input)
            layout.addWidget(self.manual_assign_checkbox)

            # Виконавець
            self.worker_input = QComboBox()
            self.workers_map = {}
            self.worker_input.addItem("— Немає виконавця —")
            self.workers_map["— Немає виконавця —"] = None
            for w in Employee.select().where(Employee.is_active == True):
                label = f"{w.full_name} (ID {w.id})"
                self.worker_input.addItem(label)
                self.workers_map[label] = w

            current_worker_key = next(
                (k for k, w in self.workers_map.items() if
                 w and task.assigned_worker and w.id == task.assigned_worker.id),
                "— Немає виконавця —"
            )
            self.worker_input.setCurrentText(current_worker_key)
            self._add_row(layout, "Виконавець:", self.worker_input)

            # Чекбокс для вводу дати вручну
            self.manual_issue_date_checkbox = QCheckBox("Ввести дату вручну")
            self.manual_issue_date_checkbox.stateChanged.connect(self.toggle_issue_date_input)
            layout.addWidget(self.manual_issue_date_checkbox)

            # Поле дати
            self.issue_date_edit = QDateEdit()
            self.issue_date_edit.setCalendarPopup(True)
            self.issue_date_edit.setDisplayFormat("yyyy-MM-dd")
            self.issue_date_edit.setDate(self.task.issue_date or QDate.currentDate())
            self.issue_date_edit.setVisible(False)
            self._add_row(layout, "Дата видачі:", self.issue_date_edit)

            self.manual_assign_checkbox.setChecked(False)
            self.worker_input.setEnabled(False)

            # Чекбокс архівації
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

        except Exception as e:
            QMessageBox.critical(self, "Помилка ініціалізації", f"Не вдалося завантажити форму редагування:\n{e}")
            self.reject()

    def _add_row(self, layout: QVBoxLayout, label: str, widget) -> None:
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(widget)
        layout.addLayout(row)

    def _on_status_changed(self, status: str) -> None:
        if status == "completed":
            self.archive_checkbox.setChecked(True)

    def _on_maintenance_changed(self):
        if self.manual_assign_checkbox.isChecked():
            maintenance = self.maintenance_map.get(self.maintenance_input.currentText())
            if maintenance and maintenance.employee:
                target_id = maintenance.employee.id
                for i in range(self.worker_input.count()):
                    label = self.worker_input.itemText(i)
                    worker = self.workers_map.get(label)
                    if worker and worker.id == target_id:
                        self.worker_input.setCurrentIndex(i)
                        break
            else:
                self.worker_input.setCurrentText("— Немає виконавця —")

    def toggle_worker_input(self):
        is_manual = self.manual_assign_checkbox.isChecked()
        self.worker_input.setEnabled(is_manual)
        self._on_maintenance_changed()

    def update_maintenance_list(self):
        self._fill_maintenance_by_vehicle()
        self._on_maintenance_changed()

    def _fill_maintenance_by_vehicle(self):
        selected_vehicle = self.vehicles_map.get(self.vehicle_input.currentText())
        self.maintenance_input.clear()
        self.maintenance_map.clear()

        self.maintenance_input.addItem("— Немає обслуговування —")
        self.maintenance_map["— Немає обслуговування —"] = None

        for r in self.all_maintenance_records:
            if r.vehicle.id == selected_vehicle.id:
                label = f"{r.service_date} - {r.service_type}"
                self.maintenance_input.addItem(label)
                self.maintenance_map[label] = r

        current = next(
            (k for k, r in self.maintenance_map.items()
             if r and self.task.maintenance and r.id == self.task.maintenance.id),
            "— Немає обслуговування —"
        )
        self.maintenance_input.setCurrentText(current)

    def save_changes(self) -> None:
        try:
            old_status = self.task.status
            old_worker = self.task.assigned_worker

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
            self.task.assigned_worker = (
                self.workers_map[self.worker_input.currentText()]
                if self.manual_assign_checkbox.isChecked()
                else None
            )
            # Дата видачі
            if self.manual_issue_date_checkbox.isChecked():
                self.task.issue_date = self.issue_date_edit.date().toPyDate()
            else:
                self.task.issue_date = self.task.maintenance.service_date if self.task.maintenance else None

            self.task.save()
            # Якщо статус або виконавець змінився — оновлюємо навантаження
            if old_status != self.task.status or old_worker != self.task.assigned_worker:
                # Оновити для попереднього виконавця, якщо був
                if old_worker:
                    recalculate_workload(old_worker)

                # Оновити для нового виконавця, якщо є
                if self.task.assigned_worker:
                    recalculate_workload(self.task.assigned_worker)

            QMessageBox.information(self, "Успіх", "Зміни до задачі успішно збережено.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка збереження", f"Не вдалося зберегти зміни до задачі:\n{e}")

    def toggle_issue_date_input(self, state):
        try:
            self.issue_date_edit.setVisible(self.manual_issue_date_checkbox.isChecked())
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося перемкнути ручне введення дати:\n{e}")
