from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
)
from models.employee import Employee


class SelectEmployeeDialog(QDialog):
    """
    Вікно вибору працівника, який ще не має облікового запису.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Оберіть працівника")
        self.setMinimumSize(400, 300)
        self.selected_employee = None

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()

        try:
            self.employees = list(Employee.select().where(Employee.user.is_null()))
            for emp in self.employees:
                self.list_widget.addItem(f"{emp.full_name} ({emp.position.name})")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити працівників: {e}")
            self.employees = []

        layout.addWidget(QLabel("Працівники без обліковки:"))
        layout.addWidget(self.list_widget)

        btn = QPushButton("Прив’язати")
        btn.clicked.connect(self.select_employee)
        layout.addWidget(btn)

    def select_employee(self):
        index = self.list_widget.currentRow()
        if index == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть працівника зі списку.")
            return
        self.selected_employee = self.employees[index]
        self.accept()
