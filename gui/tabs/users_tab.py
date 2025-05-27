from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class UsersTab(QWidget):
    """
    Вкладка керування користувачами.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде функціонал керування користувачами.")
        layout.addWidget(label)
        self.setLayout(layout)
