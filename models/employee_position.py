from peewee import Model, CharField, TextField
from models.db import db


class EmployeePosition(Model):
    """
    Посада працівника (довідник).

    Args:
        name (str): Назва посади.
        notes (str): Додаткові примітки або опис (необов’язково).

    Returns:
        EmployeePosition: Об'єкт довідника посад.

    Raises:
        peewee.IntegrityError: Якщо вказано неунікальну назву посади.
    """
    name: str = CharField(max_length=50, unique=True)

    notes: str = TextField(null=True)

    class Meta:
        database = db
        table_name = "employee_positions"
