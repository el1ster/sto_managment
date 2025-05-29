from peewee import Model, CharField, ForeignKeyField, DateField, BooleanField
from models.db import db
from models.employee_position import EmployeePosition

class Employee(Model):
    """
    Працівник.

    Args:
        full_name (str): ПІБ.
        phone (str): Телефон.
        email (str): Email.
        hire_date (date): Дата прийому.
        position (EmployeePosition): FK на посаду.
        is_active (bool): Чи працює.
    """
    full_name = CharField(max_length=100)
    phone = CharField(max_length=20, null=True)
    email = CharField(max_length=100, null=True)
    hire_date = DateField(null=True)
    position = ForeignKeyField(EmployeePosition, backref="employees", column_name="position_id")
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = "employees"
