from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class TasksTab(QWidget):
    """
    Вкладка задач та обліку робіт.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде модуль задач та робіт.")
        layout.addWidget(label)
        self.setLayout(layout)
