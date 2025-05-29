from peewee import Model, CharField, DateField, FloatField, ForeignKeyField
from models.db import db
from models.employee import Employee

class Expense(Model):
    """
    Витрати (бухгалтерія).

    Args:
        description (str): Опис.
        date (date): Дата.
        amount (float): Сума.
        employee (Employee): Хто оформив/видаткова особа.
    """
    description = CharField(max_length=255)
    date = DateField()
    amount = FloatField()
    employee = ForeignKeyField(Employee, backref="expenses", column_name="employee_id")

    class Meta:
        database = db
        table_name = "expenses"
