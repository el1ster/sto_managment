from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QAbstractItemView, QHeaderView, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate
from models.maintenance_record import MaintenanceRecord
from gui.dialogs.add_maintenance_dialog import AddMaintenanceDialog
from gui.dialogs.edit_maintenance_dialog import EditMaintenanceDialog
from gui.dialogs.maintenance_card_dialog import MaintenanceCardDialog


class MaintenanceTab(QWidget):
    """
    Вкладка для управління записами обслуговування транспорту.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        layout = QVBoxLayout(self)

        # --- Фільтр по даті ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Період з:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-12))
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

        # --- Таблиця ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Дата", "Транспорт", "Сума", "Тип", "Коментар"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellDoubleClicked.connect(self.open_card_dialog)
        layout.addWidget(self.table)

        # --- Кнопки ---
        btns = QHBoxLayout()
        self.add_btn = QPushButton("Додати")
        self.edit_btn = QPushButton("Редагувати")
        self.delete_btn = QPushButton("Видалити")
        btns.addWidget(self.add_btn)
        btns.addWidget(self.edit_btn)
        btns.addWidget(self.delete_btn)
        layout.addLayout(btns)

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        self.delete_btn.clicked.connect(self.delete_selected)

        self.load_records()

    def load_records(self):
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            records = MaintenanceRecord.select().where(
                (MaintenanceRecord.service_date >= start) &
                (MaintenanceRecord.service_date <= end)
            )
            self.table.setRowCount(len(records))
            for row, r in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(r.service_date.strftime("%Y-%m-%d")))
                self.table.setItem(row, 1, QTableWidgetItem(r.vehicle.number_plate))
                self.table.setItem(row, 2, QTableWidgetItem(f"{r.material_cost:.2f} грн"))
                self.table.setItem(row, 3, QTableWidgetItem(r.service_type or "-"))
                self.table.setItem(row, 4, QTableWidgetItem(r.service_desc or "-"))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Помилка"])
            self.table.setItem(0, 0, QTableWidgetItem(str(e)))

    def get_selected_record(self):
        row = self.table.currentRow()
        if row == -1:
            return None

        service_date = self.table.item(row, 0).text()
        number_plate = self.table.item(row, 1).text()

        from models.vehicle import Vehicle

        return (MaintenanceRecord
                .select()
                .join(Vehicle)
                .where(
            (MaintenanceRecord.service_date == service_date) &
            (Vehicle.number_plate == number_plate)
        )
                .first())

    def open_add_dialog(self):
        try:
            print("[MaintenanceTab] Відкриття діалогу додавання")
            dlg = AddMaintenanceDialog(self)
            if dlg.exec():
                print("[MaintenanceTab] Додано новий запис — оновлення таблиці")
                self.load_records()
        except Exception as e:
            print(f"[MaintenanceTab][ERROR] Помилка додавання: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося додати запис: {e}")

    def open_edit_dialog(self):
        try:
            print("[MaintenanceTab] Спроба редагування запису")
            record = self.get_selected_record()
            if not record:
                print("[MaintenanceTab] Не вибрано жодного запису")
                QMessageBox.warning(self, "Помилка", "Оберіть запис для редагування.")
                return

            dlg = EditMaintenanceDialog(record, self)
            if dlg.exec():
                print(f"[MaintenanceTab] Запис ID={record.id} змінено — оновлення таблиці")
                self.load_records()
        except Exception as e:
            print(f"[MaintenanceTab][ERROR] Помилка редагування: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося редагувати запис: {e}")

    def delete_selected(self):
        try:
            print("[MaintenanceTab] Спроба видалення запису")
            record = self.get_selected_record()
            if not record:
                print("[MaintenanceTab] Не вибрано запис для видалення")
                QMessageBox.warning(self, "Помилка", "Оберіть запис для видалення.")
                return

            confirm = QMessageBox.question(
                self, "Підтвердження",
                f"Видалити запис обслуговування від {record.service_date}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                print(f"[MaintenanceTab] Видалення запису ID={record.id}")
                record.delete_instance()
                self.load_records()
        except Exception as e:
            print(f"[MaintenanceTab][ERROR] Помилка видалення: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося видалити запис: {e}")

    def open_card_dialog(self, row, column):
        try:
            print("[MaintenanceTab] Відкриття картки запису")
            record = self.get_selected_record()
            if not record:
                print("[MaintenanceTab] Не вибрано запис для перегляду")
                return
            dlg = MaintenanceCardDialog(record, self)
            dlg.exec()
            print("[MaintenanceTab] Картка закрита")
        except Exception as e:
            print(f"[MaintenanceTab][ERROR] Помилка відкриття картки: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити картку запису: {e}")
