from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QMenu, QPushButton,
    QCheckBox
)
from PyQt6.QtCore import QDate
from models.maintenance_record import MaintenanceRecord
from models.task import Task
from logic.accounting_utils import get_total_cost_with_tax
from gui.dialogs.maintenance_info_card_dialog import MaintenanceInfoCardDialog
from gui.dialogs.add_maintenance_dialog import AddMaintenanceDialog
from gui.dialogs.edit_maintenance_dialog import EditMaintenanceDialog
from config import ENTERPRISE_START_DATE


class NumericTableItem(QTableWidgetItem):
    def __init__(self, display_text: str, number_value: float):
        super().__init__(display_text)
        self.number_value = number_value

    def __lt__(self, other):
        if isinstance(other, NumericTableItem):
            return self.number_value < other.number_value
        return super().__lt__(other)


class MaintenanceExecutionTab(QWidget):
    """
    Вкладка "Обслуговування" для працівників СТО (виконавчий режим).
    Показує перелік обслуговувань з прив’язаними задачами.

    Args:
        parent: Батьківський віджет (необов'язково).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        try:
            self._init_filters()
            self._init_checkboxes()
            self._init_buttons()
            self._init_search()
            self._init_table()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося ініціалізувати вкладку: {e}")

    def _init_filters(self):
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Період з:"))

        self.start_date = QDateEdit()
        self.start_date.setDate(
            QDate(ENTERPRISE_START_DATE.year, ENTERPRISE_START_DATE.month, ENTERPRISE_START_DATE.day))
        self.start_date.setCalendarPopup(True)
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("по:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filter_layout.addWidget(self.end_date)

        self.layout.addLayout(filter_layout)

    def _init_checkboxes(self):
        checkbox_layout = QHBoxLayout()
        self.show_completed_checkbox = QCheckBox("Показувати завершені")
        self.show_completed_checkbox.setChecked(False)
        self.show_completed_checkbox.stateChanged.connect(self.load_data)
        checkbox_layout.addWidget(self.show_completed_checkbox)
        checkbox_layout.addStretch()
        self.layout.addLayout(checkbox_layout)

    def _init_buttons(self):
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Додати")
        add_btn.clicked.connect(self.add_record)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Редагувати")
        edit_btn.clicked.connect(self.edit_record)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Видалити")
        delete_btn.clicked.connect(self.delete_record)
        button_layout.addWidget(delete_btn)

        refresh_btn = QPushButton("Оновити")
        refresh_btn.clicked.connect(self.load_data)
        button_layout.addWidget(refresh_btn)

        self.layout.addLayout(button_layout)

    def _init_search(self):
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по стовпчикам...")
        self.search_input.textChanged.connect(self.apply_filter)
        search_layout.addWidget(QLabel("Пошук:"))
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

    def _init_table(self):
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Дата", "Авто", "Тип", "Коментар", "Без податків", "З податками", "К-сть задач", "Статус"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.open_card_dialog)
        self.layout.addWidget(self.table)

    def load_data(self):
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            records = MaintenanceRecord.select().where(
                (MaintenanceRecord.service_date >= start) &
                (MaintenanceRecord.service_date <= end)
            )

            if not self.show_completed_checkbox.isChecked():
                records = records.where(MaintenanceRecord.status != "completed")

            self.all_records = list(records)
            self.apply_filter()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити дані: {e}")

    def apply_filter(self):
        try:
            query = self.search_input.text().lower().strip()
            filtered = []

            for r in self.all_records:
                no_tax_sum = float(r.material_cost)
                with_tax_sum = get_total_cost_with_tax(r)
                task_count = Task.select().where(Task.maintenance == r).count()

                search_text = " ".join([
                    r.service_date.strftime("%Y-%m-%d"),
                    r.vehicle.number_plate,
                    r.service_type or "",
                    r.service_desc or "",
                    f"{no_tax_sum:.2f}",
                    f"{with_tax_sum:.2f}",
                    str(task_count),
                    r.status
                ]).lower()

                if query in search_text:
                    filtered.append((r, no_tax_sum, with_tax_sum, task_count))

            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(filtered))

            for row, (r, no_tax_sum, with_tax_sum, task_count) in enumerate(filtered):
                self.table.setItem(row, 0, QTableWidgetItem(r.service_date.strftime("%Y-%m-%d")))
                self.table.setItem(row, 1, QTableWidgetItem(r.vehicle.number_plate))
                self.table.setItem(row, 2, QTableWidgetItem(r.service_type or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(r.service_desc or "-"))

                item_no_tax = NumericTableItem(f"{no_tax_sum:,.2f} грн".replace(",", " "), no_tax_sum)
                self.table.setItem(row, 4, item_no_tax)

                item_with_tax = NumericTableItem(f"{with_tax_sum:,.2f} грн".replace(",", " "), with_tax_sum)
                self.table.setItem(row, 5, item_with_tax)

                item_task_count = NumericTableItem(str(task_count), task_count)
                self.table.setItem(row, 6, item_task_count)

                self.table.setItem(row, 7, QTableWidgetItem(r.status))

            self.table.setSortingEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при фільтрації: {e}")

    def open_card_dialog(self):
        try:
            row = self.table.currentRow()
            if row == -1:
                return

            date_str = self.table.item(row, 0).text()
            plate = self.table.item(row, 1).text()

            for r in self.all_records:
                if r.vehicle.number_plate == plate and r.service_date.strftime('%Y-%m-%d') == date_str:
                    dlg = MaintenanceInfoCardDialog(r, self)
                    dlg.exec()
                    return
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити картку обслуговування: {e}")

    def add_record(self):
        dlg = AddMaintenanceDialog(self)
        if dlg.exec():
            self.load_data()

    def edit_record(self):
        try:
            row = self.table.currentRow()
            if row == -1:
                QMessageBox.warning(self, "Увага", "Оберіть запис для редагування.")
                return

            date_str = self.table.item(row, 0).text()
            plate = self.table.item(row, 1).text()

            for r in self.all_records:
                if r.vehicle.number_plate == plate and r.service_date.strftime('%Y-%m-%d') == date_str:
                    dlg = EditMaintenanceDialog(r, self)
                    if dlg.exec():
                        self.load_data()
                    return
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити діалог редагування: {e}")

    def delete_record(self):
        try:
            row = self.table.currentRow()
            if row == -1:
                QMessageBox.warning(self, "Увага", "Оберіть запис для видалення.")
                return

            date_str = self.table.item(row, 0).text()
            plate = self.table.item(row, 1).text()

            for r in self.all_records:
                if r.vehicle.number_plate == plate and r.service_date.strftime('%Y-%m-%d') == date_str:
                    if Task.select().where(Task.maintenance == r).exists():
                        QMessageBox.warning(
                            self, "Видалення неможливе",
                            "Неможливо видалити запис, оскільки він має пов’язані задачі."
                        )
                        return

                    reply = QMessageBox.question(
                        self, "Підтвердження",
                        f"Ви дійсно бажаєте видалити запис від {r.service_date} ({r.vehicle.number_plate})?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        r.delete_instance(recursive=True)
                        self.load_data()
                    return
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося видалити запис: {e}")
