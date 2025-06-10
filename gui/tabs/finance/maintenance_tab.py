from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QAbstractItemView, QHeaderView, QDateEdit, QMessageBox, QLineEdit
)

from gui.dialogs.add_maintenance_dialog import AddMaintenanceDialog
from gui.dialogs.edit_maintenance_dialog import EditMaintenanceDialog
from gui.dialogs.maintenance_card_dialog import MaintenanceCardDialog
from gui.dialogs.maintenance_summary_dialog import MaintenanceSummaryDialog
from models.maintenance_record import MaintenanceRecord
from logic.accounting_utils import get_total_cost_with_tax

from datetime import date

class DateTableItem(QTableWidgetItem):
    def __init__(self, display_text: str, date_value: date | None):
        super().__init__(display_text)
        self.date_value = date_value or date.min

    def __lt__(self, other):
        if isinstance(other, DateTableItem):
            return self.date_value < other.date_value
        return super().__lt__(other)


class AmountTableItem(QTableWidgetItem):
    def __init__(self, display_text: str, amount: float):
        super().__init__(display_text)
        self.amount = amount

    def __lt__(self, other):
        if isinstance(other, AmountTableItem):
            return self.amount < other.amount
        return super().__lt__(other)


class MaintenanceTab(QWidget):
    def __init__(self, current_user, parent=None):
        try:
            super().__init__(parent)
            self.current_user = current_user
            layout = QVBoxLayout(self)

            # --- Фільтр по даті ---
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(QLabel("Період з:"))
            self.start_date = QDateEdit()
            self.start_date.setDate(QDate.currentDate().addMonths(-24))
            self.start_date.setCalendarPopup(True)
            filter_layout.addWidget(self.start_date)

            filter_layout.addWidget(QLabel("по:"))
            self.end_date = QDateEdit()
            self.end_date.setDate(QDate.currentDate())
            self.end_date.setCalendarPopup(True)
            filter_layout.addWidget(self.end_date)

            self.filter_btn = QPushButton("Показати")
            self.filter_btn.clicked.connect(self.load_records)
            filter_layout.addWidget(self.filter_btn)

            layout.addLayout(filter_layout)

            # --- Кнопки ---
            btn_layout = QHBoxLayout()
            self.add_btn = QPushButton("Додати")
            self.edit_btn = QPushButton("Редагувати")
            self.delete_btn = QPushButton("Видалити")
            btn_layout.addWidget(self.add_btn)
            btn_layout.addWidget(self.edit_btn)
            btn_layout.addWidget(self.delete_btn)
            layout.addLayout(btn_layout)

            self.add_btn.clicked.connect(self.open_add_dialog)
            self.delete_btn.clicked.connect(self.delete_selected)
            self.edit_btn.clicked.connect(self.open_edit_dialog)

            # --- Сума + пошук + кнопка ---
            total_layout = QHBoxLayout()
            self.total_label = QLabel("Сума обслуговувань: 0.00 грн")
            self.details_btn = QPushButton("Детальніше")
            self.details_btn.setMinimumWidth(150)
            self.details_btn.clicked.connect(self.show_summary_dialog)
            total_layout.addWidget(self.total_label)
            total_layout.addStretch()
            total_layout.addWidget(self.details_btn)
            layout.addLayout(total_layout)

            search_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Пошук по транспорту, типу або коментарю...")
            self.search_input.textChanged.connect(self.apply_filter)
            search_layout.addWidget(QLabel("Пошук:"))
            search_layout.addWidget(self.search_input)
            layout.addLayout(search_layout)

            self.all_records = []

            # --- Таблиця ---
            self.table = QTableWidget(0, 7)
            self.table.setHorizontalHeaderLabels([
                "Дата", "Авто", "Тип", "Коментар", "Без податків", "З податками", "Працівник"
            ])
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table.doubleClicked.connect(self.show_card)

            layout.addWidget(self.table)

            self.load_records()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося ініціалізувати вкладку обслуговування: {e}")

    def load_records(self):
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            records = list(MaintenanceRecord.select().where(
                (MaintenanceRecord.service_date >= start) &
                (MaintenanceRecord.service_date <= end)
            ))

            self.all_records = records
            self.apply_filter()

            total = sum(get_total_cost_with_tax(r) for r in records)
            self.total_label.setText(f"Сума обслуговувань: {total:,.2f} грн".replace(",", " "))
            self.details_btn.setEnabled(bool(records))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Помилка"])
            self.table.setItem(0, 0, QTableWidgetItem(str(e)))

    def apply_filter(self):
        try:
            query = self.search_input.text().lower().strip()
            filtered = []

            for r in self.all_records:
                text = f"{r.vehicle.number_plate} {r.service_type} {r.service_desc}".lower()
                if query in text:
                    filtered.append(r)

            self.table.setRowCount(len(filtered))
            for row, r in enumerate(filtered):
                no_tax_sum = float(r.material_cost)
                with_tax_sum = get_total_cost_with_tax(r)

                self.table.setSortingEnabled(False)
                self.table.setItem(row, 0, DateTableItem(r.service_date.strftime("%Y-%m-%d"), r.service_date))
                self.table.setItem(row, 1, QTableWidgetItem(r.vehicle.number_plate))
                self.table.setItem(row, 2, QTableWidgetItem(r.service_type or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(r.service_desc or "-"))
                self.table.setItem(row, 4, AmountTableItem(f"{no_tax_sum:,.2f} грн".replace(",", " "), no_tax_sum))
                self.table.setItem(row, 5, AmountTableItem(f"{with_tax_sum:,.2f} грн".replace(",", " "), with_tax_sum))
                self.table.setItem(row, 6, QTableWidgetItem(r.employee.full_name))
                self.table.setSortingEnabled(True)


        except Exception as e:
            print(f"[apply_filter][ERROR] {e}")
            QMessageBox.critical(self, "Помилка", f"Помилка при фільтрації: {e}")

    def open_add_dialog(self):
        try:
            dlg = AddMaintenanceDialog(self)
            if dlg.exec():
                self.load_records()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити діалог додавання: {e}")

    def open_edit_dialog(self):
        try:
            record = self.get_selected_record()
            if not record:
                QMessageBox.warning(self, "Помилка", "Оберіть запис для редагування.")
                return

            dlg = EditMaintenanceDialog(record, self)
            if dlg.exec():
                self.load_records()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити діалог редагування: {e}")

    def delete_selected(self):
        try:
            record = self.get_selected_record()
            if not record:
                QMessageBox.warning(self, "Помилка", "Оберіть запис для видалення.")
                return

            confirm = QMessageBox.question(
                self, "Підтвердження",
                f"Видалити запис за {record.service_date.strftime('%Y-%m-%d')} для {record.vehicle.number_plate}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                record.delete_instance()
                self.load_records()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося видалити запис: {e}")

    def get_selected_record(self):
        try:
            row = self.table.currentRow()
            if row == -1:
                return None
            plate = self.table.item(row, 1).text()
            date_str = self.table.item(row, 0).text()
            for r in self.all_records:
                if r.vehicle.number_plate == plate and r.service_date.strftime('%Y-%m-%d') == date_str:
                    return r
            return None
        except Exception as e:
            print(f"[get_selected_record][ERROR] {e}")
            return None

    def show_card(self):
        try:
            record = self.get_selected_record()
            if not record:
                return
            dlg = MaintenanceCardDialog(record, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити картку обслуговування: {e}")

    def show_summary_dialog(self):
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            dlg = MaintenanceSummaryDialog(start, end, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити звіт: {e}")
