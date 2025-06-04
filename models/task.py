from peewee import (
    Model,
    CharField,
    FloatField,
    DateTimeField,
    BooleanField,
    ForeignKeyField
)
from models.db import db
from models.vehicle import Vehicle
from models.maintenance_record import MaintenanceRecord


class Task(Model):
    """
    Завдання на виконання обслуговування.

    Args:
        name (str): Назва завдання.
        time_required (float): Очікувана тривалість виконання (години).
        status (str): Статус виконання (наприклад, 'pending').
        archived_at (datetime): Дата архівації.
        specialization (str): Спеціалізація виконавця (наприклад, "електрика").
        in_queue (bool): Чи знаходиться завдання в черзі.
        vehicle (Vehicle): Автомобіль, до якого належить завдання.
        maintenance (MaintenanceRecord): Запис обслуговування, в рамках якого створено завдання.

    Returns:
        Task: Об'єкт завдання.

    Raises:
        peewee.IntegrityError: У випадку порушення зв'язків vehicle або maintenance.
    """
    name: str = CharField(max_length=100)

    time_required: float = FloatField()

    status: str = CharField(max_length=50, default="pending")

    is_archived: bool = BooleanField(default=False)

    specialization: str = CharField(max_length=255)

    in_queue: bool = BooleanField(default=True)

    vehicle: Vehicle = ForeignKeyField(
        Vehicle,
        backref="tasks",
        column_name="vehicle_id"
    )

    maintenance: MaintenanceRecord = ForeignKeyField(
        MaintenanceRecord,
        backref="tasks",
        column_name="maintenance_id"
    )

    class Meta:
        database = db
        table_name = "tasks"
