from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QHeaderView, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from models.task import Task
from gui.dialogs.add_task_dialog import AddTaskDialog
from gui.dialogs.edit_task_dialog import EditTaskDialog
from gui.dialogs.task_card_dialog import TaskCardDialog


class TasksLoaderThread(QThread):
    data_loaded = pyqtSignal(list)

    def __init__(self, include_archived: bool = False):
        super().__init__()
        self.include_archived = include_archived

    def run(self):
        try:
            query = Task.select()
            if not self.include_archived:
                query = query.where(Task.is_archived == False)
            tasks = list(query)
            self.data_loaded.emit(tasks)
        except Exception:
            self.data_loaded.emit([])


class TasksTab(QWidget):
    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        admin_roles = ["admin", "superadmin"]
        if self.current_user.role.role_name not in admin_roles:
            layout = QVBoxLayout()
            label = QLabel("У вас немає доступу до цієї вкладки")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.setLayout(layout)
            return

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        search_layout = QHBoxLayout()

        self.add_button = QPushButton("Додати")
        self.edit_button = QPushButton("Редагувати")
        self.delete_button = QPushButton("Видалити")
        self.refresh_button = QPushButton("Оновити")

        self.add_button.clicked.connect(self.open_add_task_dialog)
        self.edit_button.clicked.connect(self.open_edit_task_dialog)
        self.delete_button.clicked.connect(self.delete_task_dialog)
        self.refresh_button.clicked.connect(self.load_tasks)

        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.refresh_button)

        # Пошук + галочка
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук по задачах...")
        self.search_edit.textChanged.connect(self.apply_filter)

        self.archive_checkbox = QCheckBox("Показувати архівовані")
        self.archive_checkbox.stateChanged.connect(self.load_tasks)

        search_layout.addWidget(QLabel("Пошук:"))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.archive_checkbox)

        # Таблиця
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Назва", "Статус", "Авто", "Спеціалізація", "Тривалість"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.show_task_card)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        main_layout.addLayout(btn_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        self.all_tasks = []
        self.load_tasks()

    def load_tasks(self):
        try:
            self.refresh_button.setEnabled(False)
            self.table.setRowCount(0)
            include_archived = self.archive_checkbox.isChecked()
            loader = TasksLoaderThread(include_archived=include_archived)
            loader.data_loaded.connect(self.on_tasks_loaded)
            loader.start()
            self.loader_thread = loader
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося завантажити задачі.")

            QMessageBox.critical(self, "Помилка", "Не вдалося завантажити задачі.")

    def on_tasks_loaded(self, tasks):
        self.refresh_button.setEnabled(True)
        self.all_tasks = tasks
        self.apply_filter()

    def apply_filter(self):
        try:
            query = self.search_edit.text().strip().lower()
            filtered = []
            for t in self.all_tasks:
                car_info = f"{t.vehicle.brand} {t.vehicle.model}" if t.vehicle else ""
                search_string = " ".join([
                    t.name.lower(),
                    t.status.lower(),
                    t.specialization.lower(),
                    car_info.lower()
                ])
                if query in search_string:
                    filtered.append(t)
            self.show_tasks(filtered)
        except Exception:
            QMessageBox.critical(self, "Помилка", "Помилка при фільтрації задач.")

    def show_tasks(self, tasks):
        self.table.setRowCount(len(tasks))
        for i, t in enumerate(tasks):
            car_info = f"{t.vehicle.brand} {t.vehicle.model}" if t.vehicle else "-"
            self.table.setItem(i, 0, QTableWidgetItem(t.name))
            self.table.setItem(i, 1, QTableWidgetItem(t.status))
            self.table.setItem(i, 2, QTableWidgetItem(car_info))
            self.table.setItem(i, 3, QTableWidgetItem(t.specialization))
            self.table.setItem(i, 4, QTableWidgetItem(f"{t.time_required:.2f} год"))

    def get_selected_task(self):
        try:
            selected = self.table.selectedItems()
            if not selected:
                return None
            row = selected[0].row()
            task_name = self.table.item(row, 0).text()
            for t in self.all_tasks:
                if t.name == task_name:
                    return t
            return None
        except Exception:
            QMessageBox.critical(self, "Помилка", "Не вдалося отримати обрану задачу.")
            return None

    def open_add_task_dialog(self):
        dlg = AddTaskDialog(current_user=self.current_user, parent=self)
        if dlg.exec():
            self.load_tasks()

    def open_edit_task_dialog(self):
        t = self.get_selected_task()
        if not t:
            QMessageBox.warning(self, "Помилка", "Оберіть задачу для редагування.")
            return
        dlg = EditTaskDialog(task=t, current_user=self.current_user, parent=self)
        if dlg.exec():
            self.load_tasks()

    def delete_task_dialog(self):
        t = self.get_selected_task()
        if not t:
            QMessageBox.warning(self, "Помилка", "Оберіть задачу для видалення.")
            return
        res = QMessageBox.question(
            self, "Підтвердження", f"Ви дійсно бажаєте видалити задачу '{t.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            try:
                t.delete_instance()
                self.load_tasks()
            except Exception as ex:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити задачу:\n{ex}")

    def show_task_card(self):
        t = self.get_selected_task()
        if not t:
            return
        dlg = TaskCardDialog(task=t, parent=self)
        dlg.exec()
