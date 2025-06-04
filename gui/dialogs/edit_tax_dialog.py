from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QMessageBox
)
from models.tax import Tax
from logic.validators import validate_tax_name


class EditTaxDialog(QDialog):
    """
    Діалогове вікно для редагування існуючого податку.

    Args:
        tax (Tax): Об'єкт податку, який потрібно редагувати.
        parent: Батьківський віджет.
    """

    def __init__(self, tax: Tax, parent=None):
        try:
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
            self.payer_input.addItem("працівник", userData="employee")
            self.payer_input.addItem("підприємство", userData="employer")
            index = self.payer_input.findData(tax.payer)
            if index >= 0:
                self.payer_input.setCurrentIndex(index)
            layout.addLayout(self._row("Платник:", self.payer_input))

            self.active_checkbox = QCheckBox("Активний")
            self.active_checkbox.setChecked(tax.is_active)
            layout.addWidget(self.active_checkbox)

            save_button = QPushButton("Зберегти")
            save_button.clicked.connect(self.save_tax)
            layout.addWidget(save_button)

            self.setLayout(layout)
        except Exception as e:
            QMessageBox.critical(None, "Помилка", f"Не вдалося ініціалізувати вікно редагування податку: {e}")

    def _row(self, label_text: str, widget) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        row.addWidget(widget)
        return row

    def save_tax(self):
        """
        Зберігає зміни до податку.
        """
        try:
            name = self.name_input.text().strip()

            if not validate_tax_name(name, parent=self, exclude_id=self.tax.id): return


            self.tax.tax_name = name
            self.tax.tax_type = self.type_input.currentText()
            self.tax.rate = self.rate_input.value()
            self.tax.is_percent = self.percent_checkbox.isChecked()
            self.tax.applies_to = self.applies_to_input.currentText()
            self.tax.payer = self.payer_input.currentData()
            self.tax.is_active = self.active_checkbox.isChecked()

            self.tax.save()
            QMessageBox.information(self, "Успіх", "Податок оновлено.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти податок: {e}")
