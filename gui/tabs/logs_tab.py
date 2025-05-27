from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class LogsTab(QWidget):
    """
    Вкладка журналу подій (логування).
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде журнал подій (логування).")
        layout.addWidget(label)
        self.setLayout(layout)
