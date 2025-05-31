from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
    QPushButton, QHBoxLayout, QMessageBox, QInputDialog,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QDialogButtonBox, QCheckBox, QScrollArea, QWidget, QHeaderView
)
from PyQt6.QtCore import Qt
from models.tax import Tax
from models.tax_group import TaxGroup
from models.tax_group_item import TaxGroupItem
from gui.dialogs.add_tax_dialog import AddTaxDialog
from gui.dialogs.edit_tax_dialog import EditTaxDialog


class TaxViewTab(QWidget):
    """
    Вкладка для перегляду довідника податків та груп податків.
    """

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        self.layout = QVBoxLayout()

        # Таблиці
        self.tax_table = QTableWidget()
        self.tax_group_table = QTableWidget()

        # Написи
        self.tax_table_label = QLabel("Податки")
        self.tax_group_table_label = QLabel("Групи податків")

        # Кнопки
        self.tax_buttons = self._init_tax_buttons()
        self.group_buttons = self._init_group_buttons()

        # Верстка
        self.layout.addWidget(self.tax_table_label)
        self.layout.addLayout(self.tax_buttons)
        self.layout.addWidget(self.tax_table)

        self.layout.addWidget(self.tax_group_table_label)
        self.layout.addLayout(self.group_buttons)
        self.layout.addWidget(self.tax_group_table)

        self.setLayout(self.layout)

        self.init_tax_table()
        self.init_group_table()
        self.load_data()

    def _init_tax_buttons(self) -> QHBoxLayout:
        """
        Створює панель керування податками з кнопками:
        [Додати] [Редагувати] [Видалити] [Оновити таблиці]
        """
        layout = QHBoxLayout()

        btn_add = QPushButton("Додати податок")
        btn_add.clicked.connect(self.add_tax)
        layout.addWidget(btn_add)

        btn_edit = QPushButton("Редагувати податок")
        btn_edit.clicked.connect(self.edit_tax)
        layout.addWidget(btn_edit)

        btn_delete = QPushButton("Видалити податок")
        btn_delete.clicked.connect(self.delete_tax)
        layout.addWidget(btn_delete)

        btn_refresh = QPushButton("Оновити таблиці")
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh)  # ➕ Додається останнім

        return layout

    def _init_group_buttons(self):
        layout = QHBoxLayout()

        btn_add = QPushButton("Додати групу")
        btn_add.clicked.connect(self.add_group)
        layout.addWidget(btn_add)

        btn_delete = QPushButton("Видалити групу")
        btn_delete.clicked.connect(self.delete_group)
        layout.addWidget(btn_delete)

        btn_edit = QPushButton("Редагувати податки в групі")
        btn_edit.clicked.connect(self.edit_group_taxes)
        layout.addWidget(btn_edit)

        return layout

    def init_tax_table(self):
        self.tax_table.setColumnCount(8)
        self.tax_table.setHorizontalHeaderLabels([
            "Назва податку", "Тип", "Ставка", "Відсоткова", "Сфера", "Активний", "Платник", "Групи"
        ])
        self.tax_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)


        header = self.tax_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def init_group_table(self):
        self.tax_group_table.setColumnCount(2)
        self.tax_group_table.setHorizontalHeaderLabels(["Група", "Податки"])
        self.tax_group_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def load_data(self):
        self.load_tax_data()
        self.load_group_data()

    def load_tax_data(self):
        taxes = Tax.select().order_by(Tax.tax_name)
        self.tax_table.setRowCount(len(taxes))

        for row_idx, tax in enumerate(taxes):
            groups = ", ".join([
                g.group.group_name for g in TaxGroupItem.select().where(TaxGroupItem.tax == tax)
            ])
            self.tax_table.setItem(row_idx, 0, QTableWidgetItem(tax.tax_name))
            self.tax_table.setItem(row_idx, 1, QTableWidgetItem(tax.tax_type))
            self.tax_table.setItem(row_idx, 2, QTableWidgetItem(f"{tax.rate:.2f}"))
            self.tax_table.setItem(row_idx, 3, QTableWidgetItem("Так" if tax.is_percent else "Ні"))
            self.tax_table.setItem(row_idx, 4, QTableWidgetItem(tax.applies_to))
            self.tax_table.setItem(row_idx, 5, QTableWidgetItem("Так" if tax.is_active else "Ні"))
            self.tax_table.setItem(row_idx, 6, QTableWidgetItem(getattr(tax, 'payer', '—')))
            self.tax_table.setItem(row_idx, 7, QTableWidgetItem(groups))

    def load_group_data(self):
        groups = TaxGroup.select().order_by(TaxGroup.group_name)
        self.tax_group_table.setRowCount(len(groups))

        for row_idx, group in enumerate(groups):
            tax_names = ", ".join([
                item.tax.tax_name for item in TaxGroupItem.select().where(TaxGroupItem.group == group)
            ])
            self.tax_group_table.setItem(row_idx, 0, QTableWidgetItem(group.group_name))
            self.tax_group_table.setItem(row_idx, 1, QTableWidgetItem(tax_names))

    def add_tax(self):
        print("[TaxViewTab] Відкрито діалог додавання податку.")
        dialog = AddTaxDialog(self)
        if dialog.exec():
            print("[TaxViewTab] ✅ Податок успішно додано.")
            self.load_data()

    def edit_tax(self):
        row = self.tax_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Помилка", "Оберіть податок для редагування.")
            return

        tax_name = self.tax_table.item(row, 0).text()
        tax = Tax.get_or_none(Tax.tax_name == tax_name)
        print(f"[TaxViewTab] 📝 Спроба редагування податку '{tax_name}'")

        if not tax:
            QMessageBox.critical(self, "Помилка", "Податок не знайдено.")
            return

        try:
            dialog = EditTaxDialog(tax, self)
            if dialog.exec():
                self.load_data()
        except Exception as e:
            print(f"[TaxViewTab] ❌ Помилка при відкритті діалогу редагування: {e}")

    def delete_tax(self):
        row = self.tax_table.currentRow()
        if row < 0:
            print("[TaxViewTab] ⚠️ Податок не обрано для видалення.")
            QMessageBox.warning(self, "Помилка", "Оберіть податок для видалення.")
            return

        name = self.tax_table.item(row, 0).text()
        print(f"[TaxViewTab] 🗑️ Спроба видалити податок '{name}'")
        confirm = QMessageBox.question(
            self,
            "Підтвердження",
            f"Ви впевнені, що хочете видалити податок '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            tax = Tax.get_or_none(Tax.tax_name == name)
            if tax:
                tax.delete_instance()
                print(f"[TaxViewTab] ✅ Податок '{name}' видалено.")
                self.load_data()

    def add_group(self):
        print("[TaxViewTab] Запит на створення нової групи податків.")
        name, ok = QInputDialog.getText(self, "Нова група", "Введіть назву групи податків:")
        if ok and name:
            TaxGroup.create(group_name=name)
            print(f"[TaxViewTab] ✅ Групу податків '{name}' додано.")
            QMessageBox.information(self, "Успіх", "Групу додано")
            self.load_data()

    def delete_group(self):
        row = self.tax_group_table.currentRow()
        if row < 0:
            print("[TaxViewTab] ⚠️ Групу податків не обрано для видалення.")
            QMessageBox.warning(self, "Помилка", "Оберіть групу для видалення.")
            return

        group_name = self.tax_group_table.item(row, 0).text()
        print(f"[TaxViewTab] 🗑️ Спроба видалити групу податків '{group_name}'")
        group = TaxGroup.get_or_none(TaxGroup.group_name == group_name)
        if not group:
            print("[TaxViewTab] ❌ Групу не знайдено.")
            QMessageBox.critical(self, "Помилка", "Групу не знайдено.")
            return

        confirm = QMessageBox.question(
            self, "Підтвердження", f"Ви дійсно хочете видалити групу '{group_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            TaxGroupItem.delete().where(TaxGroupItem.group == group).execute()
            group.delete_instance()
            print(f"[TaxViewTab] ✅ Групу '{group_name}' видалено.")
            self.load_data()

    def edit_group_taxes(self):
        row = self.tax_group_table.currentRow()
        if row < 0:
            print("[TaxViewTab] ⚠️ Групу не обрано для редагування.")
            QMessageBox.warning(self, "Помилка", "Оберіть групу для редагування.")
            return

        group_name = self.tax_group_table.item(row, 0).text()
        print(f"[TaxViewTab] 🛠️ Редагування податків у групі '{group_name}'")
        group = TaxGroup.get_or_none(TaxGroup.group_name == group_name)
        if not group:
            print("[TaxViewTab] ❌ Групу не знайдено.")
            QMessageBox.critical(self, "Помилка", "Групу не знайдено.")
            return

        dialog = EditGroupTaxesDialog(group, self)
        if dialog.exec():
            selected_ids = dialog.get_selected_tax_ids()
            TaxGroupItem.delete().where(TaxGroupItem.group == group).execute()
            for tax_id in selected_ids:
                TaxGroupItem.create(group=group, tax=tax_id)
            print(f"[TaxViewTab] ✅ Прив’язки податків до групи '{group_name}' оновлено.")
            QMessageBox.information(self, "Успіх", "Прив’язки податків оновлено.")
            self.load_data()


class EditGroupTaxesDialog(QDialog):
    def __init__(self, group: TaxGroup, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Редагування податків для групи: {group.group_name}")
        self.setMinimumSize(400, 500)

        self.group = group
        self.selected_ids = set()

        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout()

        all_taxes = list(Tax.select().order_by(Tax.tax_name))
        current_ids = {item.tax.id for item in TaxGroupItem.select().where(TaxGroupItem.group == group)}

        self.checkboxes = []

        for tax in all_taxes:
            checkbox = QCheckBox(f"{tax.tax_name} ({tax.rate} {'%' if tax.is_percent else 'грн'})")
            checkbox.tax_id = tax.id
            checkbox.setChecked(tax.id in current_ids)
            self.checkboxes.append(checkbox)
            content_layout.addWidget(checkbox)

        content.setLayout(content_layout)
        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_selected_tax_ids(self) -> list[int]:
        return [cb.tax_id for cb in self.checkboxes if cb.isChecked()]