from peewee import *
from .db import db


class TaxGroup(Model):
    """
    Група податків.

    Args:
        group_name (str): Назва групи.
    """
    group_id = AutoField(primary_key=True)  # Явно вказуємо ім’я поля
    group_name = CharField(max_length=100, unique=True)

    class Meta:
        database = db
        table_name = "tax_groups"
