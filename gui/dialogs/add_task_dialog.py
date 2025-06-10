from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QComboBox, QPushButton, QMessageBox, QCheckBox
)
from PyQt6.QtWidgets import QCheckBox, QDateEdit
from PyQt6.QtCore import QDate, Qt
from models.task import Task
from models.vehicle import Vehicle
from models.maintenance_record import MaintenanceRecord
from models.employee import Employee
from peewee import JOIN
import config


class AddTaskDialog(QDialog):
    """
    Діалогове вікно для створення нового завдання.

    Args:
        current_user: Поточний користувач.
        parent: Батьківський віджет.
    """

    def __init__(self, current_user, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle("Додати нове завдання")
            self.setMinimumSize(500, 350)
            self.current_user = current_user

            layout = QVBoxLayout()

            self.name_input = QLineEdit()
            self._add_row(layout, "Назва:", self.name_input)

            self.time_input = QDoubleSpinBox()
            self.time_input.setRange(0.1, 100.0)
            self.time_input.setSuffix(" год")
            self.time_input.setSingleStep(0.25)
            self._add_row(layout, "Тривалість:", self.time_input)

            self.status_input = QComboBox()
            self.status_input.addItems(config.TASK_STATUSES)
            self.status_input.setCurrentText("new")
            self._add_row(layout, "Статус:", self.status_input)

            self.specialization_input = QComboBox()
            self.specialization_input.addItems(config.SPECIALIZATIONS)
            self.specialization_input.setCurrentIndex(0)
            self._add_row(layout, "Спеціалізація:", self.specialization_input)

            self.vehicle_input = QComboBox()
            self.vehicles_map = {
                f"{v.brand} {v.model} ({v.number_plate})": v for v in Vehicle.select()
            }
            self.vehicle_input.addItems(self.vehicles_map.keys())
            self.vehicle_input.currentTextChanged.connect(self._on_vehicle_changed)
            self._add_row(layout, "Автомобіль:", self.vehicle_input)

            self.all_maintenance_records = list(
                MaintenanceRecord.select(MaintenanceRecord, Employee).join(Employee, JOIN.LEFT_OUTER,
                                                                           on=MaintenanceRecord.employee))

            self.maintenance_input = QComboBox()
            self.maintenance_map = {}
            self._update_maintenance_options()
            self.maintenance_input.currentTextChanged.connect(self._on_maintenance_changed)
            self._add_row(layout, "Обслуговування:", self.maintenance_input)

            self.manual_assign_checkbox = QCheckBox("Призначити виконавця вручну")
            self.manual_assign_checkbox.setChecked(False)
            self.manual_assign_checkbox.stateChanged.connect(self.toggle_worker_input)
            layout.addWidget(self.manual_assign_checkbox)

            self.worker_input = QComboBox()
            self.workers_map = {"— Немає виконавця —": None}
            self.worker_input.addItem("— Немає виконавця —")
            for w in Employee.select().where(Employee.is_active == True):
                label = f"{w.full_name} (ID {w.id})"
                self.worker_input.addItem(label)
                self.workers_map[label] = w
            self._add_row(layout, "Виконавець:", self.worker_input)
            # Чекбокс
            self.manual_issue_date_checkbox = QCheckBox("Ввести дату вручну")
            self.manual_issue_date_checkbox.stateChanged.connect(self.toggle_issue_date_input)

            # Поле дати
            self.issue_date_edit = QDateEdit()
            self.issue_date_edit.setCalendarPopup(True)
            self.issue_date_edit.setDisplayFormat("yyyy-MM-dd")
            self.issue_date_edit.setDate(QDate.currentDate())
            self.issue_date_edit.setVisible(False)

            self._add_row(layout, "Дата видачі:", self.manual_issue_date_checkbox)
            self._add_row(layout, "", self.issue_date_edit)

            self.toggle_worker_input()

            btns = QHBoxLayout()
            save_btn = QPushButton("Зберегти")
            save_btn.clicked.connect(self.save_task)
            cancel_btn = QPushButton("Скасувати")
            cancel_btn.clicked.connect(self.reject)
            btns.addWidget(save_btn)
            btns.addWidget(cancel_btn)

            layout.addLayout(btns)
            self.setLayout(layout)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка ініціалізації форми:\n{e}")

    def _add_row(self, layout: QVBoxLayout, label: str, widget) -> None:
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(widget)
        layout.addLayout(row)

    def _on_vehicle_changed(self):
        try:
            self._update_maintenance_options()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити список обслуговувань:\n{e}")

    def _update_maintenance_options(self):
        self.maintenance_input.blockSignals(True)
        self.maintenance_input.clear()
        self.maintenance_map.clear()

        self.maintenance_input.addItem("— Немає обслуговування —")
        self.maintenance_map["— Немає обслуговування —"] = None

        selected_vehicle = self.vehicles_map.get(self.vehicle_input.currentText())
        for r in self.all_maintenance_records:
            if selected_vehicle and r.vehicle.id == selected_vehicle.id:
                label = f"{r.service_date} - {r.service_type}"
                self.maintenance_input.addItem(label)
                self.maintenance_map[label] = r

        self.maintenance_input.setCurrentIndex(0)
        self.maintenance_input.blockSignals(False)

    def _on_maintenance_changed(self, text: str):
        try:
            if not self.manual_assign_checkbox.isChecked():
                return

            record = self.maintenance_map.get(text)
            employee = getattr(record, "employee", None) if record else None
            if not employee:
                self.worker_input.setCurrentText("— Немає виконавця —")
                return

            target_id = employee.id
            for i in range(self.worker_input.count()):
                label = self.worker_input.itemText(i)
                worker = self.workers_map.get(label)
                if worker and worker.id == target_id:
                    self.worker_input.setCurrentIndex(i)
                    break
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити виконавця:\n{e}")

    def toggle_worker_input(self):
        try:
            is_manual = self.manual_assign_checkbox.isChecked()
            self.worker_input.setEnabled(is_manual)
            self._on_maintenance_changed(self.maintenance_input.currentText())
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при перемиканні режиму призначення:\n{e}")

    def save_task(self) -> None:
        try:
            name = self.name_input.text().strip()
            time = self.time_input.value()
            status = self.status_input.currentText()
            specialization = self.specialization_input.currentText()

            if self.manual_issue_date_checkbox.isChecked():
                issue_date = self.issue_date_edit.date().toPyDate()
            else:
                record = self.maintenance_map[self.maintenance_input.currentText()]
                issue_date = record.service_date if record else date.today()

            if not name or not specialization:
                QMessageBox.warning(self, "Помилка", "Заповніть усі обов’язкові поля.")
                return

            vehicle = self.vehicles_map[self.vehicle_input.currentText()]
            maintenance = self.maintenance_map[self.maintenance_input.currentText()]
            worker = (
                self.workers_map[self.worker_input.currentText()]
                if self.manual_assign_checkbox.isChecked()
                else None
            )

            Task.create(
                name=name,
                time_required=time,
                status=status,
                specialization=specialization,
                vehicle=vehicle,
                maintenance=maintenance,
                assigned_worker=worker,
                issue_date=issue_date,
                is_archived=(status == "completed")
            )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти задачу:\n{e}")

    def toggle_issue_date_input(self, state):
        try:
            if hasattr(self, "issue_date_edit"):
                self.issue_date_edit.setVisible(self.manual_issue_date_checkbox.isChecked())
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося перемкнути ручне введення дати:\n{e}")


