from peewee import Model, CharField, TextField
from models.db import db

class UserRole(Model):
    """
    Довідник ролей користувачів.

    Args:
        role_name (str): Назва ролі.
        description (str): Опис ролі.
    """
    role_name = CharField(max_length=50, unique=True)
    description = TextField(null=True)

    class Meta:
        database = db
        table_name = "user_roles"
