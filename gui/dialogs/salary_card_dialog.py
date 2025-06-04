from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QFormLayout, QFrame
)
from models.salary_record import SalaryRecord
from logic.tax_utils import split_tax_breakdown


class SalaryCardDialog(QDialog):
    """
    Картка запису про заробітну плату з деталізацією податків.
    """

    def __init__(self, record: SalaryRecord, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Картка зарплати")
        self.setMinimumSize(520, 500)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        print("[SalaryCardDialog] Ініціалізація вікна для:", record.employee.full_name)

        try:
            print("[SalaryCardDialog] Створення вкладки 'Інформація'")
            info_tab = QWidget()
            form = QFormLayout()

            form.addRow("Працівник:", QLabel(record.employee.full_name))
            form.addRow("Місяць:", QLabel(record.salary_month.strftime("%Y-%m")))

            self._add_divider(form)
            self._add_section_title(form, "Зарплатна інформація")

            print("[SalaryCardDialog] Зарплата:", record.base_salary, "+", record.bonus)
            total = (record.base_salary or 0) + (record.bonus or 0)
            form.addRow("Ставка:", QLabel(f"{record.base_salary:.2f} грн"))
            form.addRow("Бонус:", QLabel(f"{record.bonus:.2f} грн"))
            form.addRow("Разом:", QLabel(f"{total:.2f} грн"))

            print("[SalaryCardDialog] Отримання податкового навантаження...")
            employer_taxes, employee_taxes = split_tax_breakdown(record)
            print("[SalaryCardDialog] Податки підприємства:", employer_taxes)
            print("[SalaryCardDialog] Податки працівника:", employee_taxes)

            self._add_divider(form)
            self._add_section_title(form, "Податки (підприємство)")
            total_employer = sum(employer_taxes.values())
            form.addRow("Разом:", QLabel(f"{total_employer:.2f} грн"))
            for name, value in employer_taxes.items():
                form.addRow(f"— {name}:", QLabel(f"{value:.2f} грн"))

            self._add_divider(form)
            self._add_section_title(form, "Податки (працівник)")
            total_employee = sum(employee_taxes.values())
            form.addRow("Разом:", QLabel(f"{total_employee:.2f} грн"))
            for name, value in employee_taxes.items():
                form.addRow(f"— {name}:", QLabel(f"{value:.2f} грн"))

            print("[SalaryCardDialog] Підрахунок виплат")
            self._add_divider(form)
            self._add_section_title(form, "Підсумки")
            net_payout = total - total_employee
            bank_payout = total + total_employer
            form.addRow("Сума на руки:", QLabel(f"{net_payout:.2f} грн"))
            form.addRow("Сума до виплати через банк:", QLabel(f"{bank_payout:.2f} грн"))

            if record.comment:
                self._add_divider(form)
                self._add_section_title(form, "📝 Коментар")
                form.addRow(QLabel(record.comment))

            info_tab.setLayout(form)
            tabs.addTab(info_tab, "Інформація")

        except Exception as e:
            print(f"[SalaryCardDialog][ERROR] {e}")
            error_tab = QWidget()
            error_layout = QVBoxLayout()
            error_layout.addWidget(QLabel(f"Помилка завантаження картки: {e}"))
            error_tab.setLayout(error_layout)
            tabs.addTab(error_tab, "Інформація")

        layout.addWidget(tabs)
        print("[SalaryCardDialog] Картка зарплати готова.")

    def _add_divider(self, form: QFormLayout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        form.addRow(line)

    def _add_section_title(self, form: QFormLayout, title: str):
        label = QLabel(f"<b>{title}</b>")
        form.addRow(label)
