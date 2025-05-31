from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QMessageBox
)
from models.tax import Tax


class EditTaxDialog(QDialog):
    """
    Діалогове вікно для редагування існуючого податку.

    Args:
        tax (Tax): Об'єкт податку, який потрібно редагувати.
        parent: Батьківський віджет.
    """

    def __init__(self, tax: Tax, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Редагування податку: {tax.tax_name}")
        self.setMinimumSize(400, 300)
        self.tax = tax

        layout = QVBoxLayout()

        self.name_input = QLineEdit(tax.tax_name)
        layout.addLayout(self._row("Назва податку:", self.name_input))

        self.type_input = QComboBox()
        self.type_input.addItems(["прибутковий", "соціальний", "екологічний", "інше"])
        self.type_input.setCurrentText(tax.tax_type)
        layout.addLayout(self._row("Тип:", self.type_input))

        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0, 1_000_000)
        self.rate_input.setDecimals(2)
        self.rate_input.setValue(tax.rate)
        layout.addLayout(self._row("Ставка:", self.rate_input))

        self.percent_checkbox = QCheckBox("Відсоткова ставка (%)")
        self.percent_checkbox.setChecked(tax.is_percent)
        layout.addWidget(self.percent_checkbox)

        self.applies_to_input = QComboBox()
        self.applies_to_input.addItems(["зарплата", "транспорт"])
        self.applies_to_input.setCurrentText(tax.applies_to)
        layout.addLayout(self._row("Сфера:", self.applies_to_input))

        self.payer_input = QComboBox()
        self.payer_input.addItems(["employee", "employer"])
        self.payer_input.setCurrentText(tax.payer)
        layout.addLayout(self._row("Платник:", self.payer_input))

        self.active_checkbox = QCheckBox("Активний")
        self.active_checkbox.setChecked(tax.is_active)
        layout.addWidget(self.active_checkbox)

        save_button = QPushButton("Зберегти")
        save_button.clicked.connect(self.save_tax)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def _row(self, label_text: str, widget) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        row.addWidget(widget)
        return row

    def save_tax(self):
        """
        Зберігає зміни до податку та виводить лог у консоль.
        """
        name = self.name_input.text().strip()
        if not name:
            print("[EditTaxDialog] ❌ Назва податку не вказана.")
            QMessageBox.warning(self, "Помилка", "Введіть назву податку.")
            return

        print(f"[EditTaxDialog] 📝 Оновлення податку '{self.tax.tax_name}' на '{name}'")

        self.tax.tax_name = name
        self.tax.tax_type = self.type_input.currentText()
        self.tax.rate = self.rate_input.value()
        self.tax.is_percent = self.percent_checkbox.isChecked()
        self.tax.applies_to = self.applies_to_input.currentText()
        self.tax.payer = self.payer_input.currentText()
        self.tax.is_active = self.active_checkbox.isChecked()

        print(f"[EditTaxDialog] ➕ Тип: {self.tax.tax_type}")
        print(f"[EditTaxDialog] ➕ Ставка: {self.tax.rate} {'%' if self.tax.is_percent else 'грн'}")
        print(f"[EditTaxDialog] ➕ Сфера: {self.tax.applies_to}")
        print(f"[EditTaxDialog] ➕ Платник: {self.tax.payer}")
        print(f"[EditTaxDialog] ➕ Активний: {self.tax.is_active}")

        self.tax.save()
        print(f"[EditTaxDialog] ✅ Податок '{self.tax.tax_name}' збережено.")

        QMessageBox.information(self, "Успіх", "Податок оновлено.")
        self.accept()

