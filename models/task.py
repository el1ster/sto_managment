from peewee import (
    Model, CharField, FloatField, DateField, BooleanField,
    ForeignKeyField
)
from models.db import db
from models.vehicle import Vehicle
from models.maintenance_record import MaintenanceRecord
from models.employee import Employee
from datetime import date


class Task(Model):
    """
    Завдання на виконання обслуговування.

    Args:
        name (str): Назва завдання.
        time_required (float): Очікувана тривалість виконання (години).
        status (str): Статус виконання.
        specialization (str): Необхідна спеціалізація.
        in_queue (bool): Чи в черзі на розподіл.
        vehicle (Vehicle): Пов’язане авто.
        maintenance (MaintenanceRecord): Пов’язане обслуговування.
        assigned_worker (Employee): Призначений працівник (опційно).
        is_archived (bool): Чи архівоване.
        issue_date (date): Дата створення.
    """

    name = CharField(max_length=100)
    time_required = FloatField()
    status = CharField(max_length=50, default="pending")
    specialization = CharField(max_length=255)
    in_queue = BooleanField(default=True)

    vehicle = ForeignKeyField(Vehicle, backref="tasks", column_name="vehicle_id")
    maintenance = ForeignKeyField(MaintenanceRecord, backref="tasks", column_name="maintenance_id", null=True)
    assigned_worker = ForeignKeyField(Employee, backref="tasks", column_name="assigned_worker_id", null=True)

    is_archived = BooleanField(default=False)
    issue_date = DateField(default=date.today)

    class Meta:
        database = db
        table_name = "tasks"
