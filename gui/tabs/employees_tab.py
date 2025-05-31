from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QHeaderView
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from models.employee import Employee
from models.employee_position import EmployeePosition
from gui.dialogs.edit_employee_dialog import EditEmployeeDialog
from logic.validators import validate_full_name
from gui.dialogs.employee_card_dialog import EmployeeCardDialog


class EmployeesLoaderThread(QThread):
    """
    Асинхронне завантаження працівників із бази даних.
    """
    data_loaded = pyqtSignal(list)

    def run(self):
        try:
            employees = list(Employee.select().join(EmployeePosition).where(Employee.is_active == True))
            self.data_loaded.emit(employees)
        except Exception:
            self.data_loaded.emit([])


class EmployeesTab(QWidget):
    """
    Вкладка керування працівниками: CRUD, фільтрація, асинхронне завантаження.
    """

    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        admin_roles = ["admin", "superadmin"]
        if self.current_user.role.role_name not in admin_roles:
            main_layout = QVBoxLayout()
            label = QLabel("У вас немає доступу до цієї вкладки")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(label)
            self.setLayout(main_layout)
            return

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        search_layout = QHBoxLayout()

        # --- Кнопки CRUD ---
        self.add_button = QPushButton("Додати")
        self.edit_button = QPushButton("Редагувати")
        self.delete_button = QPushButton("Видалити")
        self.refresh_button = QPushButton("Оновити")

        self.add_button.clicked.connect(self.open_add_employee_dialog)
        self.edit_button.clicked.connect(self.open_edit_employee_dialog)
        self.delete_button.clicked.connect(self.delete_employee_dialog)
        self.refresh_button.clicked.connect(self.load_employees)

        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.refresh_button)

        # --- Поле пошуку ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук по стовпчикам...")
        self.search_edit.textChanged.connect(self.apply_filter)
        search_layout.addWidget(QLabel("Пошук:"))
        search_layout.addWidget(self.search_edit)

        # --- Таблиця працівників ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ПІБ", "Посада", "Телефон", "Email", "Статус"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.show_employee_card)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # --- Розміщення ---
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        self.all_employees = []
        self.load_employees()

    def load_employees(self):
        self.refresh_button.setEnabled(False)
        self.table.setRowCount(0)
        loader = EmployeesLoaderThread()
        loader.data_loaded.connect(self.on_employees_loaded)
        loader.start()
        self.loader_thread = loader

    def on_employees_loaded(self, employees):
        self.refresh_button.setEnabled(True)
        self.all_employees = employees
        self.apply_filter()

    def apply_filter(self):
        filter_text = self.search_edit.text().strip().lower()
        filtered = []
        for emp in self.all_employees:
            position_name = emp.position.name if emp.position else ""
            status = "активний" if emp.is_active else "деактивований"
            # Конкатенуємо всі потрібні поля в один рядок для пошуку
            search_string = " ".join([
                emp.full_name.lower() if emp.full_name else "",
                position_name.lower(),
                emp.phone.lower() if emp.phone else "",
                emp.email.lower() if emp.email else "",
                status
            ])
            if filter_text in search_string:
                filtered.append(emp)
        self.show_employees(filtered)

    def show_employees(self, employees):
        self.table.setRowCount(len(employees))
        for i, emp in enumerate(employees):
            self.table.setItem(i, 0, QTableWidgetItem(emp.full_name))
            position_name = emp.position.name if emp.position else ""
            self.table.setItem(i, 1, QTableWidgetItem(position_name))
            self.table.setItem(i, 2, QTableWidgetItem(emp.phone or "-"))
            self.table.setItem(i, 3, QTableWidgetItem(emp.email or "-"))
            self.table.setItem(i, 4, QTableWidgetItem("Активний" if emp.is_active else "Деактивований"))

    def get_selected_employee(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        full_name = self.table.item(row, 0).text()
        for emp in self.all_employees:
            if emp.full_name == full_name:
                return emp
        return None

    def open_add_employee_dialog(self):
        from gui.dialogs.add_employee_dialog import AddEmployeeDialog
        dlg = AddEmployeeDialog(self)
        if dlg.exec():
            self.load_employees()

    def open_edit_employee_dialog(self):
        emp = self.get_selected_employee()
        if not emp:
            QMessageBox.warning(self, "Помилка", "Оберіть працівника для редагування.")
            return
        dlg = EditEmployeeDialog(emp, self)
        if dlg.exec():
            self.load_employees()

    def delete_employee_dialog(self):
        emp = self.get_selected_employee()
        if not emp:
            QMessageBox.warning(self, "Помилка", "Оберіть працівника для видалення.")
            return
        res = QMessageBox.question(
            self, "Підтвердження", f"Ви дійсно бажаєте видалити працівника '{emp.full_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            try:
                emp.delete_instance()
                self.load_employees()
            except Exception as ex:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити працівника:\n{ex}")

    def show_employee_card(self, index):
        emp = self.get_selected_employee()
        if not emp:
            return
        dlg = EmployeeCardDialog(emp, self)
        dlg.exec()
