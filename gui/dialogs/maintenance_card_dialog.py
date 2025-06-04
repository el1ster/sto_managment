from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QFormLayout, QFrame
)
from models.maintenance_record import MaintenanceRecord
from logic.tax_utils import get_tax_breakdown


class MaintenanceCardDialog(QDialog):
    """
    Картка запису обслуговування транспорту з деталізацією.
    """

    def __init__(self, record: MaintenanceRecord, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Картка обслуговування")
        self.setMinimumSize(520, 480)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        print(f"[MaintenanceCardDialog] Відкриття картки для: {record.vehicle.number_plate}, {record.service_date}")

        try:
            info_tab = QWidget()
            form = QFormLayout()

            form.addRow("Транспорт:", QLabel(record.vehicle.number_plate))
            form.addRow("Дата:", QLabel(record.service_date.strftime("%Y-%m-%d")))
            form.addRow("Тип:", QLabel(record.service_type or "-"))

            self._add_divider(form)
            self._add_section_title(form, "Інформація про обслуговування")
            form.addRow("Сума:", QLabel(f"{record.material_cost:.2f} грн"))

            print("[MaintenanceCardDialog] Обчислення податків...")
            taxes = get_tax_breakdown(record)
            total_taxes = sum(taxes.values())

            self._add_divider(form)
            self._add_section_title(form, "Податки")
            form.addRow("Разом:", QLabel(f"{total_taxes:.2f} грн"))
            for name, value in taxes.items():
                form.addRow(f"— {name}:", QLabel(f"{value:.2f} грн"))

            self._add_divider(form)
            self._add_section_title(form, "Підсумок")
            total_payment = record.material_cost + total_taxes
            form.addRow("Сума до оплати:", QLabel(f"{total_payment:.2f} грн"))

            if record.service_desc:
                self._add_divider(form)
                self._add_section_title(form, "📝 Коментар")
                form.addRow(QLabel(record.service_desc))


            info_tab.setLayout(form)
            tabs.addTab(info_tab, "Інформація")

        except Exception as e:
            print(f"[MaintenanceCardDialog][ERROR] {e}")
            error_tab = QWidget()
            error_layout = QVBoxLayout()
            error_layout.addWidget(QLabel(f"Помилка завантаження картки: {e}"))
            error_tab.setLayout(error_layout)
            tabs.addTab(error_tab, "Інформація")

        layout.addWidget(tabs)
        print("[MaintenanceCardDialog] Картка готова.")

    def _add_divider(self, form: QFormLayout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        form.addRow(line)

    def _add_section_title(self, form: QFormLayout, title: str):
        label = QLabel(f"<b>{title}</b>")
        form.addRow(label)
