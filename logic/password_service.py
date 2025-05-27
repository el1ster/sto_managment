"""
Логіка хешування та перевірки паролів користувача.

Усі функції цього модуля використовують бібліотеку passlib для захисту паролів.
"""

from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    """
    Хешує пароль користувача для безпечного зберігання в БД.

    Args:
        password (str): Пароль у відкритому вигляді.

    Returns:
        str: Захешований пароль, який можна зберігати у полі password_hash.

    Raises:
        ValueError: Якщо пароль не відповідає мінімальним вимогам безпеки.
    """
    # Тут можна додати додаткову перевірку складності пароля (довжина, спецсимволи)
    if not password or len(password) < 6:
        raise ValueError("Пароль повинен містити не менше 6 символів.")
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Перевіряє, чи співпадає введений пароль із захешованим значенням у БД.

    Args:
        password (str): Пароль у відкритому вигляді (який ввів користувач).
        password_hash (str): Хеш пароля із БД.

    Returns:
        bool: True — якщо пароль вірний, False — якщо не співпадає.

    Raises:
        Exception: Якщо перевірка не може бути виконана (наприклад, помилковий хеш).
    """
    return pbkdf2_sha256.verify(password, password_hash)
