from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import QThread, pyqtSignal
from datetime import date
from peewee import fn
from models.task import Task
from models.employee import Employee
from models.optimization_worker import OptimizationWorker
from logic.optimize_tasks import optimize_unassigned_tasks
from models.db import db  # Импортируем объект базы данных для транзакций


class OptimizationLoaderThread(QThread):
    data_loaded = pyqtSignal(list, list, dict, dict)

    def run(self):
        try:
            today = date.today()

            task_qs = Task.select().where(
                (Task.status == "new") & (Task.is_archived == False)
            )

            tasks = {
                task.id: {
                    "required_specialization": task.specialization,
                    "time_required": task.time_required,
                    "created_at": task.issue_date or today
                } for task in task_qs
            }

            employees = Employee.select().where(Employee.is_active == True)
            workers = {}

            for emp in employees:
                optimization_worker = OptimizationWorker.get_or_none(
                    OptimizationWorker.employee == emp
                )
                if not optimization_worker:
                    continue

                workload = (Task
                            .select(fn.SUM(Task.time_required))
                            .where(
                    (Task.status == "in progress") &
                    (Task.assigned_worker == optimization_worker.employee)
                )
                            .scalar()) or 0.0

                workers[optimization_worker.id] = {
                    "employee": emp,
                    "specialization": optimization_worker.specialization,
                    "max_hours": optimization_worker.max_hours or 0.0,
                    "workload": workload
                }

            self.data_loaded.emit(list(task_qs), list(workers.values()), tasks, workers)

        except Exception as e:
            print(f"[!] Помилка при підготовці даних: {e}")
            self.data_loaded.emit([], [], {}, {})


class OptimizationTab(QWidget):
    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        self.tasks_data = {}
        self.workers_data = {}

        self._init_ui()
        self.load_initial_data()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        header = QLabel("Оптимізація задач між працівниками")
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(header)

        self.refresh_button = QPushButton("Оновити дані")
        self.refresh_button.clicked.connect(self.load_initial_data)
        main_layout.addWidget(self.refresh_button)

        grid = QGridLayout()

        # ВЛ – задачі
        self.task_table = QTableWidget(0, 4)
        self.task_table.setHorizontalHeaderLabels(["Назва", "Спеціалізація", "Тривалість (год)", "Дата створення"])
        grid.addWidget(self._wrap_table("Задачі без виконавців", self.task_table), 0, 0)

        # ВП – працівники
        self.worker_table = QTableWidget(0, 4)
        self.worker_table.setHorizontalHeaderLabels(["ПІБ", "Спеціалізація", "Навантаження", "Ліміт годин"])
        grid.addWidget(self._wrap_table("Доступні працівники", self.worker_table), 0, 1)

        # НЛ – результат
        self.result_table = QTableWidget(0, 3)
        self.result_table.setHorizontalHeaderLabels(["Працівник", "Задача", "Тривалість"])
        grid.addWidget(self._wrap_table("Розподіл задач", self.result_table), 1, 0)

        # НП – черга
        self.queue_table = QTableWidget(0, 3)
        self.queue_table.setHorizontalHeaderLabels(["Назва задачі", "Спеціалізація", "Тривалість"])
        grid.addWidget(self._wrap_table("Черга задач", self.queue_table), 1, 1)

        main_layout.addLayout(grid)

        self.optimize_button = QPushButton("Виконати оптимізацію")
        self.optimize_button.clicked.connect(self.run_optimization)
        main_layout.addWidget(self.optimize_button)

    def _wrap_table(self, title: str, table: QTableWidget) -> QWidget:
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(table)
        container = QWidget()
        container.setLayout(layout)
        return container

    def load_initial_data(self):
        self.task_table.setRowCount(0)
        self.worker_table.setRowCount(0)
        self.result_table.setRowCount(0)
        self.queue_table.setRowCount(0)

        self.loader_thread = OptimizationLoaderThread()
        self.loader_thread.data_loaded.connect(self.populate_initial)
        self.loader_thread.start()

    def populate_initial(self, tasks, workers, tasks_dict, workers_dict):
        self.tasks_data = tasks_dict
        self.workers_data = workers_dict

        for task in tasks:
            row = self.task_table.rowCount()
            self.task_table.insertRow(row)
            self.task_table.setItem(row, 0, QTableWidgetItem(task.name))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.specialization))
            self.task_table.setItem(row, 2, QTableWidgetItem(f"{task.time_required:.2f}"))
            created_at = self.tasks_data.get(task.id, {}).get("created_at", task.issue_date or date.today())
            self.task_table.setItem(row, 3, QTableWidgetItem(created_at.strftime("%Y-%m-%d")))

        for w in workers:
            emp = w["employee"]
            row = self.worker_table.rowCount()
            self.worker_table.insertRow(row)
            self.worker_table.setItem(row, 0, QTableWidgetItem(emp.full_name))
            self.worker_table.setItem(row, 1, QTableWidgetItem(w["specialization"]))
            self.worker_table.setItem(row, 2, QTableWidgetItem(f"{w['workload']:.2f}"))
            self.worker_table.setItem(row, 3, QTableWidgetItem(f"{w['max_hours']:.2f}"))

        self.optimize_button.setEnabled(True)

    def run_optimization(self):
        self.result_table.setRowCount(0)
        self.queue_table.setRowCount(0)

        try:
            assignments, queue = optimize_unassigned_tasks(self.workers_data, self.tasks_data)

            for worker_id, task_id in assignments:
                emp = self.workers_data[worker_id]["employee"]
                task = Task.get_by_id(task_id)
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                self.result_table.setItem(row, 0, QTableWidgetItem(emp.full_name))
                self.result_table.setItem(row, 1, QTableWidgetItem(task.name))
                self.result_table.setItem(row, 2, QTableWidgetItem(f"{task.time_required:.2f}"))

            for tid in queue:
                task = Task.get_by_id(tid)
                row = self.queue_table.rowCount()
                self.queue_table.insertRow(row)
                self.queue_table.setItem(row, 0, QTableWidgetItem(task.name))
                self.queue_table.setItem(row, 1, QTableWidgetItem(task.specialization))
                self.queue_table.setItem(row, 2, QTableWidgetItem(f"{task.time_required:.2f}"))

            # Зберігаємо призначення
            with db.atomic():  # Начало транзакции, как вы уже добавили в предыдущем коде
                for worker_id, task_id in assignments:
                    emp = self.workers_data[worker_id]["employee"]
                    task = Task.get_by_id(task_id)

                    # Прив'язка виконавця до задачі
                    # Находим OptimizationWorker по Employee, как и раньше
                    opt_worker = OptimizationWorker.get(OptimizationWorker.employee == emp)

                    # ИСПРАВЛЕНИЕ: Присваиваем объект Employee, на который ссылается opt_worker.employee
                    # Это гарантирует, что assigned_worker_id получит корректный ID из таблицы Employee
                    task.assigned_worker = opt_worker.employee
                    task.status = "in progress"
                    task.in_queue = False  # Задача назначена, поэтому не в очереди (0 в БД)
                    task.save()

                # Оновлення задач у черзі
                for task_id in queue:
                    task = Task.get_by_id(task_id)
                    task.assigned_worker = None  # Если в очереди, то нет назначенного работника
                    task.status = "new"  # Можно оставить "new" или ввести "queued"
                    task.in_queue = True  # Задача в очереди (1 в БД)
                    task.save()

                # Оновлення workload кожного працівника після призначень
                for worker_id in self.workers_data:
                    emp = self.workers_data[worker_id]["employee"]
                    total = (Task
                             .select(fn.SUM(Task.time_required))
                             .where(
                        (Task.assigned_worker == emp) &
                        (Task.status == "in progress")
                    )
                             .scalar()) or 0.0

                    (OptimizationWorker
                     .update(workload=total)
                     .where(OptimizationWorker.employee == emp)
                     .execute())

            QMessageBox.information(self, "Оптимізація завершена", "Задачі успішно розподілені.")

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка під час оптимізації:\n{e}")
            self.result_table.setRowCount(0)
            self.queue_table.setRowCount(0)
