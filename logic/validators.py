from PyQt6.QtWidgets import QMessageBox
from datetime import date
import re


def validate_phone(phone: str, parent=None) -> bool:
    """
    Перевіряє формат телефону та намагається нормалізувати його до +380XXXXXXXXX.

    Args:
        phone (str): Вхідний номер.
        parent: Вікно-батько.

    Returns:
        bool: True якщо валідний номер. False якщо не вдалося привести або номер невалідний.
    """
    if not phone:
        QMessageBox.warning(parent, "Помилка", "Телефон не може бути порожнім.")
        return False

    normalized = normalize_ukrainian_phone(phone)
    if not normalized:
        QMessageBox.warning(parent, "Помилка", "Не вдалося розпізнати формат телефону.")
        return False

    if not re.match(r"^\+380\d{9}$", normalized):
        QMessageBox.warning(parent, "Помилка", "Телефон повинен бути у форматі +380XXXXXXXXX.")
        return False

    # Автозаміна у полі, якщо parent має поле phone_edit
    if hasattr(parent, "phone_edit"):
        parent.phone_edit.setText(normalized)

    return True


def validate_email(email: str, parent=None) -> bool:
    """
    Перевіряє формат email-адреси.

    Args:
        email (str): Email користувача.
        parent: Вікно-батько для QMessageBox.

    Returns:
        bool: True — якщо валідно, False — якщо ні.
    """
    if not email:
        QMessageBox.warning(parent, "Помилка", "Email не може бути порожнім.")
        return False
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
        QMessageBox.warning(parent, "Помилка", "Введіть коректний email (наприклад, name@gmail.com).")
        return False
    return True


def validate_password(password: str, parent=None) -> bool:
    """
    Перевіряє валідність пароля користувача.

    Пароль має містити:
        - не менше 8 символів
        - хоча б одну велику літеру (A-Z)
        - хоча б одну малу літеру (a-z)
        - хоча б одну цифру (0-9)

    Args:
        password (str): Пароль для перевірки.
        parent: Вікно-батько для QMessageBox.

    Returns:
        bool: True — якщо пароль валідний, False — якщо ні.
    """
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
    return True


def validate_username(username: str, parent=None) -> bool:
    """
    Валідує логін користувача.

    Дозволяється лише латиниця, цифри, підкреслення; довжина — 3-30 символів.

    Args:
        username (str): Логін для перевірки.
        parent: Вікно-батько для QMessageBox.

    Returns:
        bool: True — якщо валідно, False — якщо ні.
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
    Валідує ПІБ користувача.

    Повинно бути щонайменше два слова, кожне з великої літери, дозволено апостроф та дефіс.

    Args:
        full_name (str): ПІБ для перевірки.
        parent: Вікно-батько для QMessageBox.

    Returns:
        bool: True — якщо валідно, False — якщо ні.
    """
    if not full_name or len(full_name.split()) < 2:
        QMessageBox.warning(parent, "Помилка", "Введіть повне ім'я (мінімум ім'я та прізвище).")
        return False

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
    - Дата не може бути раніше 1990 року.

    Args:
        hire_date (date): Дата для перевірки.
        parent: Вікно-батько для QMessageBox.

    Returns:
        bool: True — якщо валідно, False — якщо ні.
    """
    if not hire_date:
        QMessageBox.warning(parent, "Помилка", "Виберіть дату прийому на роботу.")
        return False
    if hire_date > date.today():
        QMessageBox.warning(parent, "Помилка", "Дата прийому не може бути у майбутньому.")
        return False
    if hire_date.year < 2021:
        QMessageBox.warning(parent, "Помилка", "Дата прийому не може бути раніше 2021 року.")
        return False
    return True


def normalize_ukrainian_phone(phone: str) -> str | None:
    """
    Нормалізує український номер телефону до формату +380XXXXXXXXX.

    Args:
        phone (str): Вхідний номер телефону.

    Returns:
        str | None: Нормалізований номер або None, якщо неможливо привести.
    """
    import re
    digits = re.sub(r'\D', '', phone)

    if len(digits) == 10 and digits.startswith("0"):
        return "+38" + digits
    elif len(digits) == 12 and digits.startswith("380"):
        return "+" + digits
    return None


def validate_vehicle_number(number: str, parent=None) -> bool:
    if not number:
        QMessageBox.warning(parent, "Помилка", "Номер авто не може бути порожнім.")
        return False
    if not re.match(r"^[А-ЯA-Z0-9\s-]{5,12}$", number, re.IGNORECASE):
        QMessageBox.warning(parent, "Помилка", "Невірний формат номерного знаку.")
        return False
    return True


def validate_vehicle_brand(brand: str, parent=None) -> bool:
    if not brand:
        QMessageBox.warning(parent, "Помилка", "Марка авто не може бути порожньою.")
        return False
    return True


def validate_vehicle_model(model: str, parent=None) -> bool:
    if not model:
        QMessageBox.warning(parent, "Помилка", "Модель авто не може бути порожньою.")
        return False
    return True


def validate_tax_name(name: str, parent=None, exclude_id: int | None = None) -> bool:
    """
    Перевіряє назву податку на унікальність та коректність.

    Args:
        name (str): Назва податку.
        parent: Вікно-батько для QMessageBox.
        exclude_id (int | None): ID податку, який редагується (щоб не враховувати себе).

    Returns:
        bool: True — якщо валідно, False — якщо ні.
    """
    if not name or len(name.strip()) < 3:
        QMessageBox.warning(parent, "Помилка", "Назва податку має містити щонайменше 3 символи.")
        return False

    from models.tax import Tax
    query = Tax.select().where(Tax.tax_name == name)
    if exclude_id:
        query = query.where(Tax.id != exclude_id)

    if query.exists():
        QMessageBox.warning(parent, "Помилка", "Податок з такою назвою вже існує.")
        return False

    return True
