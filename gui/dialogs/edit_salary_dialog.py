from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QDateEdit,
    QDoubleSpinBox, QTextEdit, QPushButton, QMessageBox
)
from models.salary_record import SalaryRecord
from models.employee import Employee
from models.tax_group import TaxGroup


class EditSalaryDialog(QDialog):
    """
    Діалог для редагування запису про заробітну плату.
    """

    def __init__(self, salary: SalaryRecord, parent=None):
        super().__init__(parent)
        self.salary = salary
        self.setWindowTitle("Редагувати запис про зарплату")
        self.setMinimumSize(420, 360)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # --- Працівник (не редагується) ---
        self.employee_combo = QComboBox()
        self.employee_combo.addItem(salary.employee.full_name)
        self.employee_combo.setEnabled(False)
        form.addRow("Працівник:", self.employee_combo)

        # --- Місяць ---
        self.month_edit = QDateEdit()
        self.month_edit.setCalendarPopup(True)
        self.month_edit.setDate(salary.salary_month)
        form.addRow("Місяць:", self.month_edit)

        # --- Зарплата + бонус ---
        self.base_spin = QDoubleSpinBox()
        self.base_spin.setRange(0, 1_000_000)
        self.base_spin.setSuffix(" грн")
        self.base_spin.setValue(float(salary.base_salary))
        form.addRow("Базова ЗП:", self.base_spin)

        self.bonus_spin = QDoubleSpinBox()
        self.bonus_spin.setRange(0, 1_000_000)
        self.bonus_spin.setSuffix(" грн")
        self.bonus_spin.setValue(float(salary.bonus))
        form.addRow("Бонус:", self.bonus_spin)

        # --- Податкова група ---
        self.tax_group_combo = QComboBox()
        self.tax_groups = list(TaxGroup.select())
        self.tax_group_combo.addItem("Без групи")
        self.tax_group_combo.addItems([g.group_name for g in self.tax_groups])
        if salary.tax_group:
            for i, g in enumerate(self.tax_groups):
                if g.group_id == salary.tax_group.group_id:  # <-- ВАЖЛИВО
                    self.tax_group_combo.setCurrentIndex(i + 1)
                    break
        form.addRow("Група податків:", self.tax_group_combo)

        # --- Коментар ---
        self.comment_edit = QTextEdit()
        self.comment_edit.setText(salary.comment or "")
        form.addRow("Коментар:", self.comment_edit)

        layout.addLayout(form)

        # --- Кнопка ---
        btn = QPushButton("Зберегти зміни")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

    def save(self):
        try:
            self.salary.salary_month = self.month_edit.date().toPyDate()
            self.salary.base_salary = self.base_spin.value()
            self.salary.bonus = self.bonus_spin.value()
            self.salary.comment = self.comment_edit.toPlainText()

            index = self.tax_group_combo.currentIndex()
            self.salary.tax_group = None if index == 0 else self.tax_groups[index - 1]

            self.salary.save()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти зміни: {e}")
