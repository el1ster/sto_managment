from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QCheckBox
)
from models.user import User
from models.role import UserRole
from logic.validators import validate_username


class EditUserDialog(QDialog):
    """
    Діалог для редагування існуючого користувача.
    """

    @staticmethod
    def allowed_to_edit(user, current_user):
        """
        Проверка права на редактирование.
        """
        if user.role.role_name == "superadmin" and user.id != current_user.id:
            return False, "Редагування чужого супер-адміну заборонено!"
        if user.role.role_name == "admin" and current_user.role.role_name != "superadmin":
            return False, "Редагування адміністратора дозволено лише супер-адміну!"
        return True, ""

    def __init__(self, user: User, current_user, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Редагувати користувача: {user.username}")
        self.setFixedSize(360, 320)
        self.user = user
        self.current_user = current_user

        layout = QVBoxLayout()
        self.username_edit = QLineEdit(user.username)

        self.role_combo = QComboBox()
        # Не даємо редагувати superadmin (id == 1), кроме самого суперадмина
        self.roles = [role for role in UserRole.select() if
                      role.role_name != "superadmin" or user.role.role_name == "superadmin"]
        self.role_combo.addItems([role.role_name for role in self.roles])
        current_index = 0
        for idx, role in enumerate(self.roles):
            if role.id == user.role.id:
                current_index = idx
                break
        self.role_combo.setCurrentIndex(current_index)

        self.active_checkbox = QCheckBox("Активний")
        self.active_checkbox.setChecked(user.is_active)

        layout.addWidget(QLabel("Логін:"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Роль:"))
        layout.addWidget(self.role_combo)
        layout.addWidget(self.active_checkbox)

        self.save_btn = QPushButton("Зберегти зміни")
        self.save_btn.clicked.connect(self.save_user)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

    from logic.validators import validate_username

    def save_user(self):
        role_index = self.role_combo.currentIndex()
        role = self.roles[role_index]
        is_active = self.active_checkbox.isChecked()
        new_username = self.username_edit.text().strip()

        # Валідатор логіну (з QMessageBox всередині)
        if not validate_username(new_username, parent=self):
            return

        # Перевірка унікальності (але дозволяємо зберегти, якщо не міняли логін)
        exists = User.select().where(
            (User.username == new_username) & (User.id != self.user.id)
        ).exists()
        if exists:
            QMessageBox.warning(self, "Помилка", "Користувач із таким логіном вже існує.")
            return

        try:
            self.user.username = new_username
            self.user.role = role
            self.user.is_active = is_active
            self.user.save()
            QMessageBox.information(self, "Успіх", "Дані користувача оновлено.")
            self.accept()
        except Exception as ex:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити користувача: {ex}")
