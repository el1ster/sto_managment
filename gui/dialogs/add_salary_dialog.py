from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QDateEdit,
    QDoubleSpinBox, QTextEdit, QPushButton, QMessageBox, QLineEdit
)
from models.salary_record import SalaryRecord
from models.employee import Employee
from models.tax_group import TaxGroup
from datetime import date


class AddSalaryDialog(QDialog):
    """
    Діалог для додавання нової зарплатної виплати з пошуком працівника і вибором податкової групи.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати запис про зарплату")
        self.setMinimumSize(420, 360)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # --- Пошук працівника ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук працівника...")
        self.search_edit.textChanged.connect(self.filter_employee)
        form.addRow("Пошук:", self.search_edit)

        # --- Працівник ---
        self.employee_combo = QComboBox()
        self.employees = list(Employee.select().where(Employee.is_active == True))
        self.filtered_employees = self.employees.copy()
        self.update_employee_combo()
        form.addRow("Працівник:", self.employee_combo)

        # --- Місяць ---
        self.month_edit = QDateEdit()
        self.month_edit.setDate(date.today())
        self.month_edit.setCalendarPopup(True)
        form.addRow("Місяць:", self.month_edit)

        # --- Зарплата + бонус ---
        self.base_spin = QDoubleSpinBox()
        self.base_spin.setRange(0, 1_000_000)
        self.base_spin.setSuffix(" грн")
        form.addRow("Базова ЗП:", self.base_spin)

        self.bonus_spin = QDoubleSpinBox()
        self.bonus_spin.setRange(0, 1_000_000)
        self.bonus_spin.setSuffix(" грн")
        form.addRow("Бонус:", self.bonus_spin)

        # --- Податкова група ---
        self.tax_group_combo = QComboBox()
        self.tax_groups = list(TaxGroup.select())
        self.tax_group_combo.addItem("Без групи")
        self.tax_group_combo.addItems([g.group_name for g in self.tax_groups])
        form.addRow("Група податків:", self.tax_group_combo)

        # --- Коментар ---
        self.comment_edit = QTextEdit()
        form.addRow("Коментар:", self.comment_edit)

        layout.addLayout(form)

        # --- Кнопка ---
        btn = QPushButton("Зберегти")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

    def update_employee_combo(self):
        self.employee_combo.clear()
        self.employee_combo.addItems([e.full_name for e in self.filtered_employees])

    def filter_employee(self, text: str):
        text = text.strip().lower()
        self.filtered_employees = [
            e for e in self.employees if text in e.full_name.lower()
        ]
        self.update_employee_combo()

    def save(self):
        try:
            if not self.filtered_employees:
                QMessageBox.warning(self, "Помилка", "Працівника не обрано.")
                return

            employee = self.filtered_employees[self.employee_combo.currentIndex()]
            tax_group = (
                None if self.tax_group_combo.currentIndex() == 0
                else self.tax_groups[self.tax_group_combo.currentIndex() - 1]
            )

            SalaryRecord.create(
                employee=employee,
                salary_month=self.month_edit.date().toPyDate(),
                base_salary=self.base_spin.value(),
                bonus=self.bonus_spin.value(),
                tax_group=tax_group,
                comment=self.comment_edit.toPlainText()
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити запис: {e}")
