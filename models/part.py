from peewee import Model, CharField, IntegerField, BooleanField
from models.db import db

class Part(Model):
    """
    Запчастина.

    Args:
        name (str): Назва.
        stock (int): Залишок на складі.
        is_active (bool): В обігу чи списана.
    """
    name = CharField(max_length=100)
    stock = IntegerField(default=0)
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = "parts"
