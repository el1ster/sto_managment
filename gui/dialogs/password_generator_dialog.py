from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
import random
import string
import pyperclip


class PasswordGeneratorDialog(QDialog):
    """
    Діалогове вікно для генерації пароля з налаштуванням параметрів.
    """

    password_generated = pyqtSignal(str)

    def __init__(self, min_length: int = 8, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle("Генератор паролів")
            self.setFixedSize(360, 280)
            self.min_length = min_length

            layout = QVBoxLayout()

            self.generated_edit = QLineEdit()
            self.generated_edit.setReadOnly(True)

            self.length_spin = QSpinBox()
            self.length_spin.setMinimum(min_length)
            self.length_spin.setMaximum(64)
            self.length_spin.setValue(12)

            self.uppercase_cb = QCheckBox("Великі літери (A-Z)")
            self.uppercase_cb.setChecked(True)
            self.lowercase_cb = QCheckBox("Малі літери (a-z)")
            self.lowercase_cb.setChecked(True)
            self.digits_cb = QCheckBox("Цифри (0-9)")
            self.digits_cb.setChecked(True)
            self.symbols_cb = QCheckBox("Спецсимволи (!@#$...)")
            self.symbols_cb.setChecked(False)

            layout.addWidget(QLabel("Згенерований пароль:"))
            layout.addWidget(self.generated_edit)

            layout.addWidget(QLabel("Довжина пароля:"))
            layout.addWidget(self.length_spin)

            layout.addWidget(self.uppercase_cb)
            layout.addWidget(self.lowercase_cb)
            layout.addWidget(self.digits_cb)
            layout.addWidget(self.symbols_cb)

            button_layout = QHBoxLayout()
            self.generate_btn = QPushButton("🔁 Згенерувати")
            self.copy_btn = QPushButton("📋 Копіювати")
            self.insert_btn = QPushButton("📥 Вставити")

            self.generate_btn.clicked.connect(self.generate_password)
            self.copy_btn.clicked.connect(self.copy_password)
            self.insert_btn.clicked.connect(self.return_password)

            button_layout.addWidget(self.generate_btn)
            button_layout.addWidget(self.copy_btn)
            button_layout.addWidget(self.insert_btn)

            layout.addLayout(button_layout)
            self.setLayout(layout)
        except Exception as e:
            QMessageBox.critical(None, "Помилка", f"Не вдалося ініціалізувати генератор паролів: {e}")

    def generate_password(self):
        try:
            length = self.length_spin.value()

            pools = []
            required_chars = []

            if self.uppercase_cb.isChecked():
                pools.append(string.ascii_uppercase)
                required_chars.append(random.choice(string.ascii_uppercase))
            if self.lowercase_cb.isChecked():
                pools.append(string.ascii_lowercase)
                required_chars.append(random.choice(string.ascii_lowercase))
            if self.digits_cb.isChecked():
                pools.append(string.digits)
                required_chars.append(random.choice(string.digits))
            if self.symbols_cb.isChecked():
                symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
                pools.append(symbols)
                required_chars.append(random.choice(symbols))

            if not pools:
                QMessageBox.warning(self, "Помилка", "Оберіть хоча б один тип символів.")
                return

            all_chars = ''.join(pools)
            remaining_length = length - len(required_chars)

            if remaining_length < 0:
                QMessageBox.warning(self, "Помилка", "Довжина пароля замала для вибраних параметрів.")
                return

            password_chars = required_chars + random.choices(all_chars, k=remaining_length)
            random.shuffle(password_chars)

            self.generated_edit.setText(''.join(password_chars))
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося згенерувати пароль: {e}")

    def copy_password(self):
        try:
            password = self.generated_edit.text()
            if password:
                pyperclip.copy(password)
                QMessageBox.information(self, "Скопійовано", "Пароль скопійовано в буфер обміну.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося скопіювати пароль: {e}")

    def return_password(self):
        try:
            password = self.generated_edit.text()
            if password:
                self.password_generated.emit(password)
                self.accept()
            else:
                QMessageBox.warning(self, "Помилка", "Спочатку згенеруйте пароль.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося передати пароль: {e}")
