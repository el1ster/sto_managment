from peewee import Model, CharField, BooleanField, ForeignKeyField, DateTimeField
from models.db import db
from models.role import UserRole

class User(Model):
    """
    Користувачі ПЗ.

    Args:
        username (str): Логін.
        password_hash (str): Хеш пароля.
        employee_id (int/None): FK на Employee.
        role (UserRole): FK на роль.
        is_active (bool): Активний.
        last_login (datetime): Дата/час останнього входу.
    """
    username = CharField(max_length=50, unique=True)
    password_hash = CharField(max_length=255)
    employee_id = CharField(max_length=50, null=True)  # або ForeignKeyField, якщо потрібно
    role = ForeignKeyField(UserRole, backref="users", column_name="role_id")
    is_active = BooleanField(default=True)
    last_login = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = "users"
