from peewee import Model, CharField, TextField
from models.db import db


class UserRole(Model):
    """
    Роль користувача в системі (довідник).

    Args:
        role_name (str): Назва ролі користувача (унікальна).
        description (str): Опис ролі (необов’язково).

    Returns:
        UserRole: Об'єкт довідника ролей.

    Raises:
        peewee.IntegrityError: Якщо спроба створити неунікальну роль.
    """
    role_name: str = CharField(max_length=50, unique=True)

    description: str = TextField(null=True)

    class Meta:
        database = db
        table_name = "user_roles"
