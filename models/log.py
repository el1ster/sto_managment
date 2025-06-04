from peewee import Model, DateTimeField, CharField, ForeignKeyField
from models.db import db
from models.user import User


class Log(Model):
    """
    Журнал дій користувачів.

    Args:
        user (User): Користувач, який виконав дію.
        action (str): Опис дії, яку було виконано.
        created_at (datetime): Дата й час виконання дії.

    Returns:
        Log: Об'єкт журналу подій.

    Raises:
        peewee.IntegrityError: Якщо не існує відповідного користувача.
    """
    user: User = ForeignKeyField(
        User,
        backref="logs",
        column_name="user_id",
        null=False
    )
    action: str = CharField(max_length=255, null=False)
    created_at: DateTimeField = DateTimeField(null=False)

    class Meta:
        database = db
        table_name = "logs"
