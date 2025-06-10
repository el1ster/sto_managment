from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QFormLayout, QMessageBox
)
from models.maintenance_record import MaintenanceRecord
from models.task import Task


class MaintenanceInfoCardDialog(QDialog):
    """
    Діалогова картка технічної інформації про обслуговування (без фінансів).

    Args:
        record (MaintenanceRecord): Запис обслуговування для перегляду.
        parent: Батьківський віджет (необов'язково).
    """

    def __init__(self, record: MaintenanceRecord, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Картка обслуговування — технічна інформація")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        # --- Основна інформація ---
        info_group = QGroupBox("Загальна інформація")
        info_layout = QFormLayout()

        info_layout.addRow("Дата обслуговування:", QLabel(record.service_date.strftime("%Y-%m-%d")))
        info_layout.addRow("Авто:", QLabel(
            f"{record.vehicle.number_plate} ({record.vehicle.brand} {record.vehicle.model})"
        ))
        info_layout.addRow("Тип послуги:", QLabel(record.service_type or "-"))
        info_layout.addRow("Працівник:", QLabel(record.employee.full_name))
        info_layout.addRow("Коментар:", QLabel(record.service_desc or "-"))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # --- Зв'язані задачі ---
        tasks_group = QGroupBox("Зв'язані задачі")
        task_table = QTableWidget()
        task_table.cellDoubleClicked.connect(self.open_task_card)
        self.task_table = task_table  # зберігаємо посилання на таблицю
        self.tasks = list(Task.select().where(Task.maintenance == record))
        task_table.setColumnCount(4)
        task_table.setHorizontalHeaderLabels(["Назва", "Статус", "Тривалість (год)", "Виконавець"])
        task_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        task_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        try:
            tasks = Task.select().where(Task.maintenance == record)
            task_table.setRowCount(len(tasks))
            for i, task in enumerate(tasks):
                task_table.setItem(i, 0, QTableWidgetItem(task.name))
                task_table.setItem(i, 1, QTableWidgetItem(task.status))
                time_text = f"{task.time_required:.2f}" if task.time_required is not None else "—"
                task_table.setItem(i, 2, QTableWidgetItem(time_text))
                task_table.setItem(i, 3, QTableWidgetItem(
                    task.assigned_worker.employee.full_name if task.assigned_worker and task.assigned_worker.employee else "—"
                ))
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити задачі:\n{e}")

        tasks_group_layout = QVBoxLayout()
        tasks_group_layout.addWidget(task_table)
        tasks_group.setLayout(tasks_group_layout)
        layout.addWidget(tasks_group)

    def open_task_card(self, row: int, column: int):
        try:
            from gui.dialogs.task_card_dialog import TaskCardDialog
            task = self.tasks[row]
            dlg = TaskCardDialog(task, self, disable_vehicle_open=True)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити картку задачі:\n{e}")
