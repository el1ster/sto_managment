from peewee import Model, DateTimeField, CharField, ForeignKeyField
from models.db import db
from models.user import User

class Log(Model):
    """
    Журнал дій.

    Args:
        user (User): Користувач.
        action (str): Опис дії.
        created_at (datetime): Коли виконано.
    """
    user = ForeignKeyField(User, backref="logs", column_name="user_id")
    action = CharField(max_length=255)
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = "logs"
