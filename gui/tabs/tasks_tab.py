from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget
from PyQt6.QtCore import QThread, pyqtSignal

class TasksLoaderThread(QThread):
    data_loaded = pyqtSignal(list)
    def run(self):
        try:
            # tasks = list(Task.select())
            tasks = [{"name": "ТО-10000", "status": "Виконано"}]  # тестова заглушка
            self.data_loaded.emit(tasks)
        except Exception:
            self.data_loaded.emit([])

class TasksTab(QWidget):
    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        layout = QVBoxLayout()
        self.refresh_button = QPushButton("Оновити задачі")
        self.refresh_button.clicked.connect(self.load_tasks)
        self.list_widget = QListWidget()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.load_tasks()

    def load_tasks(self):
        self.refresh_button.setEnabled(False)
        self.list_widget.clear()
        self.list_widget.addItem("Завантаження...")

        self.loader_thread = TasksLoaderThread()
        self.loader_thread.data_loaded.connect(self.on_tasks_loaded)
        self.loader_thread.start()

    def on_tasks_loaded(self, tasks):
        self.refresh_button.setEnabled(True)
        self.list_widget.clear()
        if not tasks:
            self.list_widget.addItem("Задач немає або сталася помилка")
            return
        for task in tasks:
            self.list_widget.addItem(f"{task.get('name', '')} | {task.get('status', '')}")
