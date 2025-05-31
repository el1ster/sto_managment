from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QMessageBox
)
from models.tax import Tax


class AddTaxDialog(QDialog):
    """
    Діалогове вікно для додавання нового податку.

    Args:
        parent: Батьківський віджет (необов'язковий).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати новий податок")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        layout.addLayout(self._row("Назва податку:", self.name_input))

        self.type_input = QComboBox()
        self.type_input.addItems(["прибутковий", "соціальний", "екологічний", "інше"])
        layout.addLayout(self._row("Тип:", self.type_input))

        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0, 1_000_000)
        self.rate_input.setDecimals(2)
        layout.addLayout(self._row("Ставка:", self.rate_input))

        self.percent_checkbox = QCheckBox("Відсоткова ставка (%)")
        layout.addWidget(self.percent_checkbox)

        self.applies_to_input = QComboBox()
        self.applies_to_input.addItems(["зарплата", "транспорт"])
        layout.addLayout(self._row("Сфера:", self.applies_to_input))

        self.payer_input = QComboBox()
        self.payer_input.addItems(["employee", "employer"])
        layout.addLayout(self._row("Платник:", self.payer_input))

        self.active_checkbox = QCheckBox("Активний")
        layout.addWidget(self.active_checkbox)

        add_button = QPushButton("Додати")
        add_button.clicked.connect(self.add_tax)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def _row(self, label_text: str, widget) -> QHBoxLayout:
        """
        Повертає горизонтальне розташування для поля з підписом.

        Args:
            label_text (str): Текст підпису.
            widget: Ввідний віджет.

        Returns:
            QHBoxLayout: Рядок з підписом і полем.
        """
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        row.addWidget(widget)
        return row

    def add_tax(self):
        """
        Обробник натискання кнопки "Додати".
        Перевіряє валідність введених даних і створює запис у базі.
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Помилка", "Введіть назву податку.")
            return

        Tax.create(
            tax_name=name,
            tax_type=self.type_input.currentText(),
            rate=self.rate_input.value(),
            is_percent=self.percent_checkbox.isChecked(),
            applies_to=self.applies_to_input.currentText(),
            payer=self.payer_input.currentText(),
            is_active=self.active_checkbox.isChecked()
        )

        QMessageBox.information(self, "Успіх", "Податок додано.")
        self.accept()
