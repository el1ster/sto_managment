from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class OptimizationTab(QWidget):
    """
    Вкладка оптимізації і планування.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Тут буде модуль оптимізації та планування.")
        layout.addWidget(label)
        self.setLayout(layout)
