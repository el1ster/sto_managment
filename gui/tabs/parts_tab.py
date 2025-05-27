from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PartsTab(QWidget):
    """
    Вкладка обліку запчастин і складу.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде модуль запчастин і складу.")
        layout.addWidget(label)
        self.setLayout(layout)
