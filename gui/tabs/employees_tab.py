from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal
# from models.employee import Employee  # додай свою модель

class EmployeesLoaderThread(QThread):
    data_loaded = pyqtSignal(list)

    def run(self):
        try:
            # employees = list(Employee.select())
            employees = [{"full_name": "Test Employee", "position": "Механік"}]  # тестова заглушка
            self.data_loaded.emit(employees)
        except Exception:
            self.data_loaded.emit([])

class EmployeesTab(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити список працівників")
        self.refresh_button.clicked.connect(self.load_employees)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_employees()

    def load_employees(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = EmployeesLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_employees_loaded)
        self.loader_thread.start()

    def on_employees_loaded(self, employees):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not employees:
            self.list_widget.addItem("Немає працівників або сталася помилка")
            return
        for emp in employees:
            self.list_widget.addItem(f"{emp.get('full_name', '')} | {emp.get('position', '')}")
