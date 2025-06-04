from peewee import (
    Model,
    CharField,
    BooleanField,
    ForeignKeyField,
    DateTimeField
)
from models.db import db
from models.role import UserRole


class User(Model):
    """
    Користувач програмного забезпечення.

    Args:
        username (str): Унікальний логін користувача.
        password_hash (str): Хеш пароля користувача.
        role (UserRole): Роль користувача в системі.
        is_active (bool): Ознака активності облікового запису.
        last_login (datetime): Час останнього входу (опціонально).

    Returns:
        User: Об'єкт користувача.

    Raises:
        peewee.IntegrityError: Якщо логін неунікальний або порушено зовнішні ключі.
    """
    username: str = CharField(max_length=50, unique=True)
    password_hash: str = CharField(max_length=255)
    role: UserRole = ForeignKeyField(
        UserRole,
        backref="users",
        column_name="role_id",
        null=False
    )
    is_active: bool = BooleanField(default=True)
    last_login: DateTimeField = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = "users"
