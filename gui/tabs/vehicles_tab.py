from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class VehiclesTab(QWidget):
    """
    Вкладка обліку транспорту.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде облік транспорту.")
        layout.addWidget(label)
        self.setLayout(layout)
