from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class FinanceTab(QWidget):
    """
    Вкладка фінансового модуля.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде фінансовий модуль.")
        layout.addWidget(label)
        self.setLayout(layout)
