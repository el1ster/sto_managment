from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QTabWidget, QWidget, QHBoxLayout, QPushButton, QLineEdit, QMessageBox
)
from models.vehicle import Vehicle
from models.maintenance_record import MaintenanceRecord
from models.task import Task


class VehicleCardDialog(QDialog):
    def __init__(self, vehicle: Vehicle, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Картка транспорту: {vehicle.number_plate}")
        self.setMinimumSize(700, 800)
        self.vehicle = vehicle

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>Марка:</b> {vehicle.brand}"))
        layout.addWidget(QLabel(f"<b>Модель:</b> {vehicle.model}"))
        layout.addWidget(QLabel(f"<b>Рік випуску:</b> {vehicle.year or '—'}"))
        layout.addWidget(QLabel(f"<b>Номер:</b> {vehicle.number_plate}"))
        layout.addWidget(QLabel(f"<b>VIN:</b> {vehicle.vin or '—'}"))
        layout.addWidget(QLabel(f"<b>Тип:</b> {vehicle.vehicle_type or '—'}"))
        layout.addWidget(QLabel(f"<b>Підрозділ:</b> {vehicle.department or '—'}"))
        layout.addWidget(QLabel(f"<b>Пробіг:</b> {vehicle.mileage or 0} км"))

        tabs = QTabWidget()
        tabs.addTab(self._create_maintenance_tab(), "Обслуговування")
        tabs.addTab(self._create_tasks_tab(), "Завдання")
        layout.addWidget(tabs)

        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.setLayout(layout)

    def _create_maintenance_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        search_label = QLabel("Пошук:")
        self.maintenance_search_input = QLineEdit()
        self.maintenance_search_input.setPlaceholderText("Введіть ключове слово...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.maintenance_search_input)
        layout.addLayout(search_layout)

        self.maintenance_table = QTableWidget()
        self.maintenance_table.setColumnCount(5)
        self.maintenance_table.setHorizontalHeaderLabels([
            "Дата", "Працівник", "Тип послуги", "Вартість матеріалів", "Пробіг (км)"
        ])

        self.maintenance_records = list(MaintenanceRecord.select().where(
            MaintenanceRecord.vehicle == self.vehicle
        ))

        self.maintenance_search_input.textChanged.connect(self.apply_maintenance_filter)
        self.maintenance_table.cellDoubleClicked.connect(
            lambda row, _: self.open_maintenance_card(self.filtered_maintenance_records[row])
        )

        layout.addWidget(self.maintenance_table)
        tab.setLayout(layout)
        self.apply_maintenance_filter()
        return tab

    def _create_tasks_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        search_label = QLabel("Пошук:")
        self.task_search_input = QLineEdit()
        self.task_search_input.setPlaceholderText("Введіть ключове слово...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.task_search_input)
        layout.addLayout(search_layout)

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels([
            "Назва", "Статус", "Спеціалізація", "Тривалість (год)"
        ])

        self.tasks = list(Task.select().where(Task.vehicle == self.vehicle))
        self.task_search_input.textChanged.connect(self.apply_task_filter)
        self.task_table.cellDoubleClicked.connect(
            lambda row, _: self.open_task_card(self.filtered_tasks[row])
        )

        layout.addWidget(self.task_table)
        tab.setLayout(layout)
        self.apply_task_filter()
        return tab

    def apply_maintenance_filter(self):
        try:
            text = self.maintenance_search_input.text().lower().strip()
            self.filtered_maintenance_records = []

            for r in self.maintenance_records:
                combined = " ".join([
                    str(r.service_date),
                    r.employee.full_name if r.employee else "",
                    r.service_type or "",
                    f"{r.material_cost:.2f}",
                    str(r.mileage or "")
                ]).lower()
                if text in combined:
                    self.filtered_maintenance_records.append(r)

            self.maintenance_table.setRowCount(len(self.filtered_maintenance_records))
            for i, r in enumerate(self.filtered_maintenance_records):
                self.maintenance_table.setItem(i, 0, QTableWidgetItem(str(r.service_date)))
                self.maintenance_table.setItem(i, 1, QTableWidgetItem(r.employee.full_name if r.employee else "-"))
                self.maintenance_table.setItem(i, 2, QTableWidgetItem(r.service_type))
                self.maintenance_table.setItem(i, 3, QTableWidgetItem(f"{r.material_cost:.2f} грн"))
                self.maintenance_table.setItem(i, 4, QTableWidgetItem(f"{r.mileage or 0} км"))
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Помилка при фільтрації: {ex}")

    def apply_task_filter(self):
        try:
            text = self.task_search_input.text().lower().strip()
            self.filtered_tasks = []

            for t in self.tasks:
                combined = " ".join([
                    t.name,
                    t.status,
                    t.specialization,
                    f"{t.time_required:.2f}"
                ]).lower()
                if text in combined:
                    self.filtered_tasks.append(t)

            self.task_table.setRowCount(len(self.filtered_tasks))
            for i, t in enumerate(self.filtered_tasks):
                self.task_table.setItem(i, 0, QTableWidgetItem(t.name))
                self.task_table.setItem(i, 1, QTableWidgetItem(t.status))
                self.task_table.setItem(i, 2, QTableWidgetItem(t.specialization))
                self.task_table.setItem(i, 3, QTableWidgetItem(f"{t.time_required:.2f}"))
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Помилка при фільтрації задач: {ex}")

    def open_maintenance_card(self, record):
        try:
            from gui.dialogs.maintenance_card_dialog import MaintenanceCardDialog
            dlg = MaintenanceCardDialog(record, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити обслуговування: {e}")

    def open_task_card(self, task):
        try:
            from gui.dialogs.task_card_dialog import TaskCardDialog
            dlg = TaskCardDialog(task, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити задачу: {e}")
