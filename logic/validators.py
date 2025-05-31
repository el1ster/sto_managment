from PyQt6.QtWidgets import QMessageBox
import re
from datetime import date


def validate_phone(phone: str, parent=None) -> bool:
    if not phone:
        QMessageBox.warning(parent, "Помилка", "Телефон не може бути порожнім.")
        return False
    if not re.match(r"^(?:\+380|0)\d{9}$", phone):
        QMessageBox.warning(parent, "Помилка", "Введіть коректний телефон у форматі +380XXXXXXXXX або 0XXXXXXXXX.")
        return False
    return True


def validate_email(email: str, parent=None) -> bool:
    if not email:
        QMessageBox.warning(parent, "Помилка", "Email не може бути порожнім.")
        return False
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
        QMessageBox.warning(parent, "Помилка", "Введіть коректний email (наприклад, name@gmail.com).")
        return False
    return True


def validate_password(password: str, parent=None) -> bool:
    if len(password) < 8:
        QMessageBox.warning(parent, "Помилка", "Пароль має бути не менше 8 символів.")
        return False
    if not re.search(r"[A-Z]", password):
        QMessageBox.warning(parent, "Помилка", "Пароль має містити хоча б одну велику літеру.")
        return False
    if not re.search(r"[a-z]", password):
        QMessageBox.warning(parent, "Помилка", "Пароль має містити хоча б одну малу літеру.")
        return False
    if not re.search(r"\d", password):
        QMessageBox.warning(parent, "Помилка", "Пароль має містити хоча б одну цифру.")
        return False
    if not re.search(r"[^A-Za-z0-9]", password):
        QMessageBox.warning(parent, "Помилка", "Пароль має містити хоча б один спецсимвол.")
        return False
    return True


def validate_username(username: str, parent=None) -> bool:
    """
    Дозволяє лише латиницю, цифри, підкреслення, 3-30 символів.
    Показує QMessageBox при помилці.
    """
    if not username:
        QMessageBox.warning(parent, "Помилка", "Логін не може бути порожнім.")
        return False
    if not re.match(r"^[a-zA-Z0-9_]{3,30}$", username):
        QMessageBox.warning(
            parent, "Помилка",
            "Логін має складатися лише з латинських літер, цифр або підкреслення (від 3 до 30 символів)."
        )
        return False
    return True



def validate_full_name(full_name: str, parent=None) -> bool:
    """
    Валідує ПІБ (мінімум два слова, кожне слово — велика буква, далі маленькі, укр/лат).
    Показує QMessageBox при помилці.

    Args:
        full_name (str): ПІБ для перевірки.
        parent: Вікно-батько для QMessageBox.

    Returns:
        bool: True якщо валідно, False якщо помилка.
    """
    if not full_name or len(full_name.split()) < 2:
        QMessageBox.warning(parent, "Помилка", "Введіть повне ім'я (мінімум ім'я та прізвище).")
        return False

    # Регулярка: кожне слово з великої літери, далі - маленькі, апостроф/дефіс
    pattern = r"^([А-ЯІЇЄҐA-Z][а-яіїєґa-zA-Z'’\-]+)(\s[А-ЯІЇЄҐA-Z][а-яіїєґa-zA-Z'’\-]+)+$"
    if not re.match(pattern, full_name):
        QMessageBox.warning(
            parent, "Помилка",
            "ПІБ має містити мінімум два слова, кожне з великої літери, дозволено апостроф, дефіс."
        )
        return False

    return True



def validate_hire_date(hire_date: date, parent=None) -> bool:
    """
    Перевіряє коректність дати прийому на роботу:
    - Дата не може бути у майбутньому.
    - Дата не може бути раніше 1990 року (опціонально, для реалістичності).

    Args:
        hire_date (date): Дата для перевірки.
        parent: Вікно-батько для QMessageBox.

    Returns:
        bool: True якщо валідно, False якщо ні.
    """
    if not hire_date:
        QMessageBox.warning(parent, "Помилка", "Виберіть дату прийому на роботу.")
        return False

    if hire_date > date.today():
        QMessageBox.warning(parent, "Помилка", "Дата прийому не може бути у майбутньому.")
        return False

    if hire_date.year < 1990:
        QMessageBox.warning(parent, "Помилка", "Дата прийому не може бути раніше 1990 року.")
        return False

    return True
