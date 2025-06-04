from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFormLayout, QDialogButtonBox, QFrame
)
from PyQt6.QtCore import Qt
from decimal import Decimal

from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord
from logic.tax_utils import split_tax_breakdown


class OperationCardDialog(QDialog):
    """
    Діалогове вікно з деталізацією запису операції (зарплата або обслуговування).

    Args:
        record: Об'єкт SalaryRecord або MaintenanceRecord.
        parent: Вікно-батько (необов'язкове).
    """

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Карта облікової операції")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        form = QFormLayout()
        layout.addLayout(form)

        print(f"[INFO] Відкрито карту операції для запису типу: {type(record).__name__}")

        def add_section_title(title: str):
            title_label = QLabel(f"<b>{title}</b>")
            title_label.setStyleSheet("margin-top: 10px;")
            form.addRow(title_label)

        def add_divider():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            form.addRow(line)

        if isinstance(record, SalaryRecord):
            self.setWindowTitle("Карта запису: Зарплата")
            form.addRow("Працівник:", QLabel(record.employee.full_name))
            form.addRow("Місяць:", QLabel(record.salary_month.strftime("%Y-%m")))

            add_divider()
            add_section_title("Зарплатна інформація")

            form.addRow("Ставка:", QLabel(f"{record.base_salary:.2f} грн"))
            form.addRow("Бонус:", QLabel(f"{record.bonus:.2f} грн"))
            form.addRow("Разом:", QLabel(f"{(record.base_salary + record.bonus):.2f} грн"))

            employer_taxes, employee_taxes = split_tax_breakdown(record)

            add_divider()
            add_section_title("Податки (підприємство)")
            total_employer = sum(employer_taxes.values())
            form.addRow("Разом:", QLabel(f"{total_employer:.2f} грн"))
            for name, value in employer_taxes.items():
                form.addRow(f"— {name}:", QLabel(f"{value:.2f} грн"))

            add_divider()
            add_section_title("Податки (працівник)")
            total_employee = sum(employee_taxes.values())
            form.addRow("Разом:", QLabel(f"{total_employee:.2f} грн"))
            for name, value in employee_taxes.items():
                form.addRow(f"— {name}:", QLabel(f"{value:.2f} грн"))

            add_divider()
            add_section_title("Підсумки")
            net_payout = (record.base_salary or 0) + (record.bonus or 0) - total_employee
            bank_payout = (record.base_salary or 0) + (record.bonus or 0) + total_employer
            form.addRow("Сума на руки:", QLabel(f"{net_payout:.2f} грн"))
            form.addRow("Сума до виплати через банк:", QLabel(f"{bank_payout:.2f} грн"))

            if record.comment:
                add_divider()
                add_section_title("📝 Коментар")
                form.addRow(QLabel(record.comment))


        elif isinstance(record, MaintenanceRecord):

            material = Decimal(record.material_cost or 0)

            print(f"[INFO] Працівник: {record.employee.full_name if record.employee else '—'}")

            print(f"[INFO] Тип обслуговування: {record.service_type}, Матеріали: {material}")

            self.setWindowTitle("Карта запису: Обслуговування")

            # Загальна інформація

            form.addRow("Дата:", QLabel(record.service_date.strftime("%Y-%m-%d")))

            form.addRow("Тип обслуговування:", QLabel(record.service_type or "—"))

            form.addRow("Працівник:", QLabel(record.employee.full_name if record.employee else "—"))

            add_divider()

            add_section_title("Загальна інформація")

            form.addRow("Вартість матеріалів:", QLabel(f"{material:.2f} грн"))

            # Податки (підприємство)

            employer, _ = split_tax_breakdown(record)

            total_employer_tax = sum(employer.values())

            print(f"[INFO] Податки підприємства: {total_employer_tax:.2f}")

            add_divider()

            add_section_title("Податки (підприємство)")

            form.addRow("Разом:", QLabel(f"{total_employer_tax:.2f} грн"))

            for name, value in employer.items():
                form.addRow(f"— {name}:", QLabel(f"{value:.2f} грн"))

            # Підсумки

            total_cost = material + total_employer_tax

            print(f"[INFO] Загальна сума: {total_cost:.2f}")

            add_divider()

            add_section_title("Підсумки")

            form.addRow("До сплати підприємством:", QLabel(f"{total_cost:.2f} грн"))

            if record.service_desc:
                print(f"[INFO] Опис: {record.service_desc}")

                add_divider()

                form.addRow("Опис:", QLabel(record.service_desc))

        button_box = QDialogButtonBox()
        close_btn = button_box.addButton("Закрити", QDialogButtonBox.ButtonRole.RejectRole)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
