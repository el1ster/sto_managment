from peewee import Model, CharField, TextField
from models.db import db

class EmployeePosition(Model):
    """
    Довідник посад працівників.

    Args:
        name (str): Назва посади.
        notes (str): Опис/примітки.
    """
    name = CharField(max_length=50, unique=True)
    notes = TextField(null=True)

    class Meta:
        database = db
        table_name = "employee_positions"
