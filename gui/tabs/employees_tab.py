from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class EmployeesTab(QWidget):
    """
    Вкладка керування працівниками.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде функціонал керування працівниками.")
        layout.addWidget(label)
        self.setLayout(layout)
