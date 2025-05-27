from peewee import Model, CharField, IntegerField, BooleanField, DateTimeField, ForeignKeyField
from models.db import db


class User(Model):
    """
    Модель користувача системи.

    Attributes:
        id (int): Первинний ключ.
        username (str): Логін користувача (унікальний).
        password_hash (str): Хеш пароля.
        employee_id (int): Зовнішній ключ на співробітника (може бути NULL).
        role_id (int): Зовнішній ключ на роль користувача.
        is_active (bool): Статус користувача (активний/деактивований).
        last_login (datetime): Дата та час останнього входу.
    """
    username = CharField(unique=True, max_length=50)
    password_hash = CharField(max_length=255)
    employee_id = IntegerField(null=True)
    role_id = IntegerField()
    is_active = BooleanField(default=True)
    last_login = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = 'users'
