from PyQt6.QtWidgets import QMessageBox

# Словарь с наборами ролей для разных функций/вкладок
ROLE_GROUPS = {
    "all": [
        "superadmin", "admin", "accountant", "owner", "master", "mechanic", "storekeeper", "viewer"
    ],
    "superadmins": ["superadmin"],
    "admins": ["admin", "superadmin"],
    "users_manage": ["admin", "superadmin"],
    "tasks": ["admin", "superadmin", "mechanic", "master", "accountant", "owner"],
    # добавь по аналогии другие наборы
}

def requires_role(group):
    """Декоратор для ограничения доступа по группе ролей."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Получаем роль текущего пользователя (имя роли)
            user_role = getattr(self, "current_user", None)
            if user_role is not None and hasattr(user_role, "role"):
                role_name = user_role.role.role_name
            elif user_role is not None and hasattr(user_role, "role_name"):
                role_name = user_role.role_name
            else:
                role_name = None

            # Получаем список допустимых ролей по группе
            allowed_roles = ROLE_GROUPS[group] if isinstance(group, str) else group

            if role_name not in allowed_roles:
                QMessageBox.warning(self, "Доступ заборонено", "У вас немає прав для цієї дії!")
                return
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
