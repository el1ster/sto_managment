"""
Модуль для авторизації користувачів та роботи з обліковими записами.

Функції:
    authenticate_user — перевірка логіна й пароля користувача.
    reset_user_password — скидання пароля для обраного користувача.
"""

from models.user import User
from logic.password_service import hash_password, verify_password


def authenticate_user(username: str, password: str) -> User | None:
    """
    Перевіряє логін і пароль користувача.

    Args:
        username (str): Логін користувача.
        password (str): Пароль у відкритому вигляді.

    Returns:
        User | None: Об'єкт користувача, якщо авторизація успішна, або None.
    """
    try:
        user = User.get_or_none(User.username == username)
        if user and verify_password(password, user.password_hash):
            return user
        return None
    except Exception:
        return None


def reset_user_password(user_id: int, new_password: str) -> bool:
    """
    Скидає (оновлює) пароль користувача за його ID.

    Args:
        user_id (int): Ідентифікатор користувача у базі даних.
        new_password (str): Новий пароль у відкритому вигляді.

    Returns:
        bool: True — якщо пароль успішно оновлено, False — у разі помилки або якщо користувача не знайдено.
    """
    try:
        user = User.get_or_none(User.id == user_id)
        if not user:
            return False
        user.password_hash = hash_password(new_password)
        user.save()
        return True
    except Exception:
        return False
