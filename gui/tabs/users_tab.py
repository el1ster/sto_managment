from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QHeaderView
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from models.user import User
from models.role import UserRole
from models.employee import Employee
from gui.dialogs.add_user_dialog import AddUserDialog
from gui.dialogs.reset_password_dialog import ResetPasswordDialog
from gui.dialogs.edit_user_dialog import EditUserDialog
from gui.dialogs.admin_confirm_dialog import AdminConfirmDialog
from gui.dialogs.user_card_dialog import UserCardDialog


class UsersLoaderThread(QThread):
    data_loaded = pyqtSignal(list)

    def run(self):
        try:
            users = list(User.select())
            self.data_loaded.emit(users)
        except Exception:
            self.data_loaded.emit([])


class UsersTab(QWidget):
    def __init__(self, current_user, main_window=None):
        super().__init__()
        self.current_user = current_user
        self.main_window = main_window

        admin_roles = ["admin", "superadmin"]
        if self.current_user.role.role_name not in admin_roles:
            main_layout = QVBoxLayout()
            label = QLabel("У вас немає доступу до цієї вкладки")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(label)
            self.setLayout(main_layout)
            return

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        search_layout = QHBoxLayout()

        self.add_button = QPushButton("Додати")
        self.edit_button = QPushButton("Редагувати")
        self.delete_button = QPushButton("Видалити")
        self.reset_pass_button = QPushButton("Скинути пароль")
        self.refresh_button = QPushButton("Оновити")

        self.add_button.clicked.connect(self.open_add_user_dialog)
        self.edit_button.clicked.connect(self.open_edit_user_dialog)
        self.delete_button.clicked.connect(self.delete_user_dialog)
        self.reset_pass_button.clicked.connect(self.open_reset_password_dialog)
        self.refresh_button.clicked.connect(self.load_users)

        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.reset_pass_button)
        btn_layout.addWidget(self.refresh_button)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук по стовпчикам...")
        self.search_edit.textChanged.connect(self.apply_filter)
        search_layout.addWidget(QLabel("Пошук:"))
        search_layout.addWidget(self.search_edit)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Логін", "Роль", "Статус", "Останній вхід"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellDoubleClicked.connect(self.open_user_card)

        main_layout.addLayout(btn_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        self.all_users = []
        self.load_users()

    def load_users(self):
        try:
            self.refresh_button.setEnabled(False)
            self.table.setRowCount(0)
            loader = UsersLoaderThread()
            loader.data_loaded.connect(self.on_users_loaded)
            loader.start()
            self.loader_thread = loader
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити користувачів: {e}")

    def on_users_loaded(self, users):
        try:
            self.refresh_button.setEnabled(True)
            self.all_users = users
            self.apply_filter()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при завантаженні: {e}")

    def apply_filter(self):
        try:
            filter_text = self.search_edit.text().strip().lower()
            filtered = []
            for user in self.all_users:
                role_name = user.role.role_name if user.role else ""
                status = "активний" if user.is_active else "деактивований"
                last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "-"
                search_string = " ".join([
                    user.username.lower() if user.username else "",
                    role_name.lower(),
                    status,
                    last_login.lower()
                ])
                if filter_text in search_string:
                    filtered.append(user)
            self.show_users(filtered)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка фільтрації: {e}")

    def show_users(self, users):
        try:
            self.table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.table.setItem(i, 0, QTableWidgetItem(user.username))
                role_name = user.role.role_name if user.role else ""
                self.table.setItem(i, 1, QTableWidgetItem(role_name))
                self.table.setItem(i, 2, QTableWidgetItem("Активний" if user.is_active else "Деактивований"))
                self.table.setItem(i, 3, QTableWidgetItem(
                    user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "-"
                ))
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при відображенні користувачів: {e}")

    def get_selected_user(self):
        try:
            selected = self.table.selectedItems()
            if not selected:
                return None
            row = selected[0].row()
            username = self.table.item(row, 0).text()
            for user in self.all_users:
                if user.username == username:
                    return user
            return None
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося отримати обраного користувача: {e}")
            return None

    def open_add_user_dialog(self):
        try:
            dlg = AddUserDialog(self.current_user, self)
            if dlg.exec():
                self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при відкритті діалогу: {e}")

    def open_edit_user_dialog(self):
        try:
            user = self.get_selected_user()
            if not user:
                QMessageBox.warning(self, "Помилка", "Оберіть користувача для редагування.")
                return

            allowed, message = EditUserDialog.allowed_to_edit(user, self.current_user)
            if not allowed:
                QMessageBox.warning(self, "Помилка", message)
                return

            dlg = EditUserDialog(user, self.current_user, self)
            if dlg.exec():
                self.load_users()
                if self.main_window:
                    self.main_window.current_user = User.get_by_id(self.current_user.id)
                    self.main_window.update_user_status()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при редагуванні: {e}")

    def delete_user_dialog(self):
        try:
            user = self.get_selected_user()
            if not user:
                QMessageBox.warning(self, "Помилка", "Оберіть користувача для видалення.")
                return

            if user.role_id == 1:
                QMessageBox.warning(self, "Помилка", "Видалення супер-адміна заборонено!")
                return

            if user.role_id == 2 and self.current_user.role_id != 1:
                QMessageBox.warning(self, "Помилка", "Видалити адміністратора може тільки супер-адмін.")
                return

            # Перевірка зовнішніх зв’язків
            employees = list(Employee.select().where(Employee.user == user))
            if employees:
                emp_names = "\n • ".join([f"{e.full_name} ({e.position.name})" for e in employees])
                QMessageBox.warning(
                    self,
                    "Видалення неможливе",
                    f"Неможливо видалити користувача, оскільки до нього прив’язані працівники:\n\n • {emp_names}"
                )
                return

            res = QMessageBox.question(
                self, "Підтвердження",
                f"Ви дійсно бажаєте видалити користувача '{user.username}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if res == QMessageBox.StandardButton.Yes:
                user.delete_instance()
                self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося видалити користувача: {e}")

    def open_reset_password_dialog(self):
        try:
            user = self.get_selected_user()
            if not user:
                QMessageBox.warning(self, "Помилка", "Оберіть користувача для скидання пароля.")
                return

            if self.current_user.role_id == 1:
                dlg = ResetPasswordDialog(user.username, self.current_user, self)
                dlg.exec()
                return

            if user.role_id == 1 or user.role_id == 2:
                confirm_dialog = AdminConfirmDialog(self)
                if confirm_dialog.exec():
                    admin_user = confirm_dialog.admin_user
                    if admin_user.role_id != 1:
                        QMessageBox.warning(self, "Помилка", "Лише SuperAdmin може виконати цю дію.")
                        return
                    dlg = ResetPasswordDialog(user.username, admin_user, self)
                    dlg.exec()
                return

            if self.current_user.role_id == 2:
                dlg = ResetPasswordDialog(user.username, self.current_user, self)
                dlg.exec()
                return

            QMessageBox.warning(self, "Помилка", "У вас немає прав для цієї дії.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося скинути пароль: {e}")

    def open_user_card(self, row, column):
        try:
            user = self.get_selected_user()
            if not user:
                QMessageBox.warning(self, "Помилка", "Не вдалося отримати користувача.")
                return

            dlg = UserCardDialog(user, self.current_user, self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити картку користувача: {e}")
