"""
Скрипт для створення тестових користувачів у базі даних системи СТО.

Використовує Peewee ORM та функції хешування паролів із logic/password_service.py.

Перед запуском:
    - Переконайся, що драйвер PyMySQL встановлений (pip install PyMySQL)
    - Всі міграції/таблиці створені у БД
    - Усі модулі імпортуються без помилок

Запускати цей скрипт тільки ОДИН раз, щоб не створити дублі!
"""

from models.user import User
from logic.password_service import hash_password
from models.db import db

# Список тестових користувачів (логін, пароль, роль)
test_users = [
    {"username": "superadmin", "password": "SuperPass1!", "role_id": 1},  # SuperAdmin
    {"username": "admin1", "password": "AdminPass1!", "role_id": 2},  # Admin
    {"username": "owner1", "password": "OwnerPass1!", "role_id": 3},  # Owner
    {"username": "accountant1", "password": "AccPass1!", "role_id": 4},  # Accountant
    {"username": "master1", "password": "MasterPass1!", "role_id": 5},  # Master
    {"username": "mechanic1", "password": "MechPass1!", "role_id": 6},  # Mechanic
    {"username": "storekeeper1", "password": "StorePass1!", "role_id": 7},  # Storekeeper
    {"username": "viewer1", "password": "ViewPass1!", "role_id": 8},  # Viewer
]


def create_test_users():
    """
    Створює тестових користувачів у таблиці users.
    Перевіряє, чи користувач із таким логіном вже існує, щоб не створювати дублікати.

    Returns:
        None
    """
    with db.atomic():  # Гарантує транзакцію на рівні БД
        for u in test_users:
            # Перевірка — якщо користувач вже є, пропустити
            existing = User.get_or_none(User.username == u["username"])
            if existing:
                print(f"[!] Користувач '{u['username']}' вже існує. Пропускаємо.")
                continue

            # Створення нового користувача з хешованим паролем
            User.create(
                username=u["username"],
                password_hash=hash_password(u["password"]),
                employee_id=None,
                role_id=u["role_id"],
                is_active=True,
                last_login=None
            )
            print(f"[+] Додано користувача '{u['username']}' з роллю {u['role_id']}.")

    print("\n[✓] Створення тестових користувачів завершено.")


if __name__ == "__main__":
    create_test_users()
