from PyQt6.QtWidgets import QMessageBox
import re

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