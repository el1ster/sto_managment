from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QHeaderView
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from models.user import User
from models.role import UserRole
from gui.dialogs.add_user_dialog import AddUserDialog
from gui.dialogs.reset_password_dialog import ResetPasswordDialog
from gui.dialogs.edit_user_dialog import EditUserDialog
from gui.dialogs.admin_confirm_dialog import AdminConfirmDialog


class UsersLoaderThread(QThread):
    """
    Асинхронне завантаження користувачів із бази даних.
    """
    data_loaded = pyqtSignal(list)

    def run(self):
        try:
            users = list(User.select())
            self.data_loaded.emit(users)
        except Exception:
            self.data_loaded.emit([])


class UsersTab(QWidget):
    """
    Вкладка керування користувачами: CRUD, скидання пароля, фільтрація.
    """

    def __init__(self, current_user, main_window=None):
        """
        Ініціалізація вкладки.

        Args:
            current_user: Об'єкт користувача, який зараз авторизований.
        """
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
            return  # Більше нічого не ініціалізуємо

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        search_layout = QHBoxLayout()

        # --- Кнопки CRUD ---
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

        # --- Поле пошуку ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук по стовпчикам...")
        self.search_edit.textChanged.connect(self.apply_filter)
        search_layout.addWidget(QLabel("Пошук:"))
        search_layout.addWidget(self.search_edit)

        # --- Таблиця користувачів ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Логін", "Роль", "Статус", "Останній вхід"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # --- Розміщення ---
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

        self.all_users = []
        self.load_users()

    def load_users(self):
        """
        Асинхронно завантажує користувачів у таблицю.
        """
        self.refresh_button.setEnabled(False)
        self.table.setRowCount(0)
        loader = UsersLoaderThread()
        loader.data_loaded.connect(self.on_users_loaded)
        loader.start()
        self.loader_thread = loader  # Не дати потоку зникнути з пам'яті

    def on_users_loaded(self, users):
        """
        Оновлює таблицю даними користувачів.

        Args:
            users (list): Список об'єктів User.
        """
        self.refresh_button.setEnabled(True)
        self.all_users = users
        self.apply_filter()

    def apply_filter(self):
        """
        Фільтрує користувачів за всіма видимими колонками.
        """
        filter_text = self.search_edit.text().strip().lower()
        filtered = []
        for user in self.all_users:
            role_name = user.role.role_name if user.role else ""
            status = "активний" if user.is_active else "деактивований"
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "-"
            # Створюємо загальний пошуковий рядок
            search_string = " ".join([
                user.username.lower() if user.username else "",
                role_name.lower(),
                status,
                last_login.lower()
            ])
            if filter_text in search_string:
                filtered.append(user)
        self.show_users(filtered)

    def show_users(self, users):
        """
        Відображає список користувачів у таблиці.

        Args:
            users (list): Список об'єктів User.
        """
        self.table.setRowCount(len(users))
        for i, user in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(user.username))
            role_name = user.role.role_name if user.role else ""
            self.table.setItem(i, 1, QTableWidgetItem(role_name))
            self.table.setItem(i, 2, QTableWidgetItem("Активний" if user.is_active else "Деактивований"))
            self.table.setItem(i, 3, QTableWidgetItem(
                user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "-"))

    def get_selected_user(self):
        """
        Повертає обраного користувача.

        Returns:
            User | None: Об'єкт користувача або None.
        """
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        username = self.table.item(row, 0).text()
        for user in self.all_users:
            if user.username == username:
                return user
        return None

    def open_add_user_dialog(self):
        dlg = AddUserDialog(self.current_user, self)
        if dlg.exec():
            self.load_users()

    def open_edit_user_dialog(self):
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Помилка", "Оберіть користувача для редагування.")
            return

        from gui.dialogs.edit_user_dialog import EditUserDialog

        # СНАЧАЛА ПРОВЕРКА ДОЗВОЛЕНОСТИ
        allowed, message = EditUserDialog.allowed_to_edit(user, self.current_user)
        if not allowed:
            QMessageBox.warning(self, "Помилка", message)
            return

        # Только теперь создаём окно
        dlg = EditUserDialog(user, self.current_user, self)
        if dlg.exec():
            self.load_users()
            if self.main_window:
                self.main_window.current_user = User.get_by_id(self.current_user.id)  # Оновити поточний user з БД
                self.main_window.update_user_status()

    def delete_user_dialog(self):
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Помилка", "Оберіть користувача для видалення.")
            return

        # Запретить удалять супер-админа вообще
        if user.role_id == 1:
            QMessageBox.warning(self, "Помилка", "Видалення супер-адміна заборонено!")
            return

        # Если удаляется админ (role_id == 2) — разрешено только суперадміну
        if user.role_id == 2 and self.current_user.role_id != 1:
            QMessageBox.warning(self, "Помилка", "Видалити адміністратора може тільки супер-адмін.")
            return

        res = QMessageBox.question(
            self, "Підтвердження", f"Ви дійсно бажаєте видалити користувача '{user.username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            try:
                user.delete_instance()
                self.load_users()
            except Exception as ex:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити користувача:\n{ex}")

    def open_reset_password_dialog(self):
        user = self.get_selected_user()
        if not user:
            QMessageBox.warning(self, "Помилка", "Оберіть користувача для скидання пароля.")
            return

        # 1. Если текущий — SuperAdmin: можно сбрасывать пароль любому без подтверждения
        if self.current_user.role_id == 1:
            dlg = ResetPasswordDialog(user.username, self.current_user, self)
            dlg.exec()
            return

        # 2. Если сбрасываешь пароль SuperAdmin'у (id == 1)
        if user.role_id == 1:
            # Обычный админ должен подтвердить супер-админа
            confirm_dialog = AdminConfirmDialog(self)
            if confirm_dialog.exec():
                admin_user = confirm_dialog.admin_user
                if admin_user.role_id != 1:
                    QMessageBox.warning(self, "Помилка", "Лише SuperAdmin може скинути пароль SuperAdmin.")
                    return
                dlg = ResetPasswordDialog(user.username, admin_user, self)
                dlg.exec()
            return

        # 3. Если сбрасываешь пароль админу (id == 2)
        if user.role_id == 2:
            # Обычный админ должен подтвердить супер-админа
            confirm_dialog = AdminConfirmDialog(self)
            if confirm_dialog.exec():
                admin_user = confirm_dialog.admin_user
                if admin_user.role_id != 1:
                    QMessageBox.warning(self, "Помилка", "Лише SuperAdmin може скинути пароль адміністратору.")
                    return
                dlg = ResetPasswordDialog(user.username, admin_user, self)
                dlg.exec()
            return

        # 4. Если обычный пользователь и текущий — Admin: сбрасываем без подтверждения
        if self.current_user.role_id == 2:
            dlg = ResetPasswordDialog(user.username, self.current_user, self)
            dlg.exec()
            return

        # 5. Остальным не даём ничего
        QMessageBox.warning(self, "Помилка", "У вас немає прав для цієї дії.")
