from peewee import Model, CharField, IntegerField, TextField
from models.db import db


class UserRole(Model):
    """
    Модель ролі користувача.

    Attributes:
        id (int): Первинний ключ.
        role_name (str): Назва ролі (унікальна).
        description (str): Опис ролі.
    """
    role_name = CharField(unique=True, max_length=50)
    description = TextField(null=True)

    class Meta:
        database = db
        table_name = 'user_roles'
