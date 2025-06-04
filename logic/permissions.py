from PyQt6.QtWidgets import QMessageBox

# Словник із групами ролей
ROLE_GROUPS = {
    "all": [
        "superadmin", "admin", "accountant", "owner", "master", "mechanic", "storekeeper", "viewer"
    ],
    "superadmins": ["superadmin"],
    "admins": ["admin", "superadmin"],
    "users_manage": ["admin", "superadmin"],
    "tasks": ["admin", "superadmin", "mechanic", "master", "accountant", "owner"],
    # TODO: Додати інші групи при потребі
}


def requires_role(group):
    """
    Декоратор для перевірки ролі користувача перед виконанням дії.

    Args:
        group (str | list): Група або список допустимих ролей.

    Returns:
        function: Обгорнута функція з перевіркою доступу.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                user_role = getattr(self, "current_user", None)
                if user_role is not None and hasattr(user_role, "role"):
                    role_name = user_role.role.role_name
                elif user_role is not None and hasattr(user_role, "role_name"):
                    role_name = user_role.role_name
                else:
                    role_name = None

                allowed_roles = ROLE_GROUPS[group] if isinstance(group, str) else group

                if role_name not in allowed_roles:
                    QMessageBox.warning(self, "Доступ заборонено", "У вас немає прав для цієї дії!")
                    return
                return func(self, *args, **kwargs)
            except Exception:
                QMessageBox.critical(self, "Помилка", "Не вдалося перевірити права доступу.")
        return wrapper
    return decorator
