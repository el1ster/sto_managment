from peewee import Model, CharField, ForeignKeyField, DateField, TextField, BooleanField
from models.db import db
from models.employee import Employee
from models.vehicle import Vehicle

class Task(Model):
    """
    Завдання/робота.

    Args:
        title (str): Назва завдання.
        description (str): Опис.
        employee (Employee): Виконавець.
        vehicle (Vehicle): Транспорт.
        deadline (date): Дедлайн.
        status (str): Статус ("нове", "в роботі", "завершено").
        is_active (bool): Актуальне/архів.
    """
    title = CharField(max_length=100)
    description = TextField(null=True)
    employee = ForeignKeyField(Employee, backref="tasks", column_name="employee_id")
    vehicle = ForeignKeyField(Vehicle, backref="tasks", column_name="vehicle_id", null=True)
    deadline = DateField(null=True)
    status = CharField(max_length=30, default="нове")
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = "tasks"
