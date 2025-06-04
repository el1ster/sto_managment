from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QHeaderView, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from models.employee import Employee
from models.employee_position import EmployeePosition
from models.optimization_worker import OptimizationWorker
from models.assignment import Assignment
from models.salary_record import SalaryRecord
from gui.dialogs.edit_employee_dialog import EditEmployeeDialog
from gui.dialogs.add_employee_dialog import AddEmployeeDialog
from logic.validators import validate_full_name
from gui.dialogs.employee_card_dialog import EmployeeCardDialog


class EmployeesLoaderThread(QThread):
    data_loaded = pyqtSignal(list)

    def __init__(self, show_inactive=False):
        super().__init__()
        self.show_inactive = show_inactive

    def run(self):
        try:
            query = Employee.select().join(EmployeePosition)
            if not self.show_inactive:
                query = query.where(Employee.is_active == True)
            query = query.order_by(EmployeePosition.name, Employee.full_name)  # сортировка по посаді, потім по ПІБ
            self.data_loaded.emit(list(query))
        except Exception:
            self.data_loaded.emit([])


class EmployeesTab(QWidget):
    def __init__(self, current_user, main_window=None):
        try:
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

            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Пошук по стовпчикам...")
            self.search_edit.textChanged.connect(self.apply_filter)
            search_layout.addWidget(QLabel("Пошук:"))
            search_layout.addWidget(self.search_edit)

            self.table = QTableWidget(0, 6)
            self.table.setHorizontalHeaderLabels(["ПІБ", "Посада", "Телефон", "Email", "Обліковка", "Статус"])
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.table.verticalHeader().setVisible(False)
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.doubleClicked.connect(self.show_employee_card)
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            self.show_inactive_checkbox = QCheckBox("Показати неактивних")
            self.show_inactive_checkbox.setChecked(False)
            self.show_inactive_checkbox.stateChanged.connect(self.load_employees)
            search_layout.addWidget(self.show_inactive_checkbox)

            main_layout.addLayout(btn_layout)
            main_layout.addLayout(search_layout)
            main_layout.addWidget(self.table)
            self.setLayout(main_layout)

            self.all_employees = []
            self.load_employees()
        except Exception as e:
            self.setLayout(QVBoxLayout())
            self.layout().addWidget(QLabel(f"Не вдалося ініціалізувати вкладку: {e}"))

    def load_employees(self):
        try:
            self.refresh_button.setEnabled(False)
            self.table.setRowCount(0)
            loader = EmployeesLoaderThread(
                show_inactive=self.show_inactive_checkbox.isChecked()
            )
            loader.data_loaded.connect(self.on_employees_loaded)
            loader.start()
            self.loader_thread = loader
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося завантажити працівників.")

    def on_employees_loaded(self, employees):
        try:
            self.refresh_button.setEnabled(True)
            self.all_employees = employees
            self.apply_filter()
        except Exception:
            QMessageBox.critical(self, "Помилка", "Помилка при оновленні таблиці працівників.")

    def apply_filter(self):
        try:
            filter_text = self.search_edit.text().strip().lower()
            filtered = []
            for emp in self.all_employees:
                try:
                    full_name = emp.full_name.lower() if emp.full_name else ""
                    position_name = emp.position.name.lower() if emp.position and emp.position.name else ""
                    phone = emp.phone.lower() if emp.phone else ""
                    email = emp.email.lower() if emp.email else ""
                    username = emp.user.username.lower() if emp.user and emp.user.username else ""
                    status = "активний" if emp.is_active else "деактивований"

                    search_string = " ".join([full_name, position_name, phone, email, username, status])
                    if filter_text in search_string:
                        filtered.append(emp)
                except Exception:
                    continue

            self.show_employees(filtered)
        except Exception:
            QMessageBox.critical(self, "Помилка", "Помилка при фільтрації.")

    def show_employees(self, employees):
        try:
            self.table.setRowCount(len(employees))
            for i, emp in enumerate(employees):
                self.table.setItem(i, 0, QTableWidgetItem(emp.full_name))
                position_name = emp.position.name if emp.position else ""
                self.table.setItem(i, 1, QTableWidgetItem(position_name))
                self.table.setItem(i, 2, QTableWidgetItem(emp.phone or "-"))
                self.table.setItem(i, 3, QTableWidgetItem(emp.email or "-"))
                username = emp.user.username if emp.user else "-"
                self.table.setItem(i, 4, QTableWidgetItem(username))
                self.table.setItem(i, 5, QTableWidgetItem("Активний" if emp.is_active else "Деактивований"))
        except Exception:
            QMessageBox.critical(self, "Помилка", "Помилка при відображенні працівників.")

    def get_selected_employee(self):
        try:
            selected = self.table.selectedItems()
            if not selected:
                return None
            row = selected[0].row()
            full_name = self.table.item(row, 0).text()
            for emp in self.all_employees:
                if emp.full_name == full_name:
                    return emp
            return None
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося отримати обраного працівника.")
            return None

    def open_add_employee_dialog(self):
        try:
            dlg = AddEmployeeDialog(current_user=self.current_user, parent=self)
            if dlg.exec():
                self.load_employees()
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося відкрити діалог додавання працівника.")

    def open_edit_employee_dialog(self):
        try:
            emp = self.get_selected_employee()
            if not emp:
                QMessageBox.warning(self, "Помилка", "Оберіть працівника для редагування.")
                return
            dlg = EditEmployeeDialog(employee=emp, current_user=self.current_user, parent=self)
            if dlg.exec():
                self.load_employees()
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося відкрити діалог редагування.")

    def delete_employee_dialog(self):
        try:
            emp = self.get_selected_employee()
            if not emp:
                QMessageBox.warning(self, "Помилка", "Оберіть працівника для видалення.")
                return

            # 🔍 Перевірка задач
            worker = OptimizationWorker.get_or_none(OptimizationWorker.employee == emp)
            if worker and Assignment.select().where(Assignment.worker == worker).exists():
                QMessageBox.warning(
                    self, "Видалення неможливе",
                    "Неможливо видалити працівника, оскільки до нього прив’язані задачі."
                )
                return

            # 💰 Перевірка зарплат
            if SalaryRecord.select().where(SalaryRecord.employee == emp).exists():
                QMessageBox.warning(
                    self, "Видалення неможливе",
                    "Неможливо видалити працівника, оскільки існують записи по зарплаті."
                )
                return

            res = QMessageBox.question(
                self, "Підтвердження",
                f"Ви дійсно бажаєте видалити працівника '{emp.full_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if res == QMessageBox.StandardButton.Yes:
                emp.delete_instance()
                self.load_employees()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при обробці видалення: {e}")

    def show_employee_card(self, index):
        try:
            emp = self.get_selected_employee()
            if not emp:
                return
            dlg = EmployeeCardDialog(emp, self)
            dlg.exec()
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося відкрити картку працівника.")
