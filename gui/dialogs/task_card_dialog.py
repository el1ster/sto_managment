from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QWidget,
    QFrame, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from models.task import Task
from gui.dialogs.vehicle_card_dialog import VehicleCardDialog
from gui.dialogs.maintenance_card_dialog import MaintenanceCardDialog
from models.maintenance_record import MaintenanceRecord


class TaskCardDialog(QDialog):
    """
    Діалогова картка для перегляду інформації про завдання з вкладками.
    """

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Картка задачі: {task.name}")
        self.setMinimumSize(600, 450)
        self.task = task

        try:
            layout = QVBoxLayout()

            tabs = QTabWidget()

            tabs.addTab(self._general_info_tab(), "Загальна")
            tabs.addTab(self._vehicle_tab(), "Транспорт")
            tabs.addTab(self._maintenance_tab(), "Обслуговування")

            layout.addWidget(tabs)

            btn_close = QPushButton("Закрити")
            btn_close.clicked.connect(self.accept)
            layout.addWidget(btn_close)

            self.setLayout(layout)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити картку задачі:\n{e}")
            self.reject()

    def _general_info_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self._info_label("Назва:", self.task.name))
        layout.addWidget(self._info_label("Тривалість:", f"{self.task.time_required:.2f} год"))
        layout.addWidget(self._info_label("Статус:", self.task.status))
        layout.addWidget(self._info_label("Спеціалізація:", self.task.specialization))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _vehicle_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        try:
            if self.task.vehicle:
                open_btn = QPushButton("Відкрити картку транспорту")
                open_btn.clicked.connect(self.open_vehicle_card)
                layout.addWidget(open_btn)

                layout.addWidget(
                    self._info_label("Марка і модель:", f"{self.task.vehicle.brand} {self.task.vehicle.model}"))
                layout.addWidget(self._info_label("Номер:", self.task.vehicle.number_plate))
                layout.addWidget(self._info_label("Тип:", self.task.vehicle.vehicle_type or "—"))
                layout.addWidget(self._info_label("VIN:", self.task.vehicle.vin or "—"))
            else:
                layout.addWidget(QLabel("Транспорт не прив'язано."))
        except Exception:
            layout.addWidget(QLabel("Невдалося отримати дані про транспорт."))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _maintenance_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        try:
            if self.task.maintenance:
                btn = QPushButton("Відкрити картку обслуговування")
                btn.clicked.connect(lambda: self.open_maintenance_card(self.task.maintenance))
                layout.addWidget(btn)
                layout.addWidget(self._info_label("Дата:", str(self.task.maintenance.service_date)))
                layout.addWidget(self._info_label("Тип послуги:", self.task.maintenance.service_type))
                layout.addWidget(
                    self._info_label("Вартість матеріалів:", f"{self.task.maintenance.material_cost:.2f} грн"))
                layout.addWidget(self._info_label("Працівник:", self.task.maintenance.employee.full_name))


            else:
                layout.addWidget(QLabel("Обслуговування не прив'язано."))
        except Exception:
            layout.addWidget(QLabel("Невдалося отримати дані про обслуговування."))

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _info_label(self, title: str, value: str) -> QWidget:
        row = QHBoxLayout()
        label = QLabel(f"<b>{title}</b>")
        text = QLabel(value)
        text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row.addWidget(label)
        row.addWidget(text)
        row.addStretch()
        frame = QFrame()
        frame.setLayout(row)
        return frame

    def open_vehicle_card(self):
        try:
            dlg = VehicleCardDialog(self.task.vehicle, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити картку транспорту: {e}")

    def open_maintenance_card(self, record):
        try:
            dlg = MaintenanceCardDialog(record, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити обслуговування: {e}")
