from peewee import (
    Model,
    CharField,
    IntegerField,
    DateTimeField,
    BooleanField
)

from models.db import db


class Vehicle(Model):
    """
    Транспортний засіб, який обслуговується у СТО.

    Args:
        vin (str): VIN-код.
        number_plate (str): Державний номер.
        brand (str): Бренд (марка).
        model (str): Модель.
        year (int): Рік випуску.
        vehicle_type (str): Тип (наприклад, легковий, мікроавтобус...).
        department (str): Відповідальний підрозділ або місце використання.
        mileage (int): Поточний пробіг.
        is_archived (datetime): Дата архівації (якщо неактивний).

    Returns:
        Vehicle: Об'єкт транспортного засобу.
    """

    vin = CharField(max_length=20, unique=True, null=False)
    number_plate = CharField(max_length=20, unique=True)
    brand = CharField(max_length=100)
    model = CharField(max_length=100)
    year = IntegerField(null=True)
    vehicle_type = CharField(max_length=50, null=True)
    department = CharField(max_length=100, null=True)
    mileage = IntegerField(null=True)
    is_archived = BooleanField(default=False)

    class Meta:
        database = db
        table_name = "vehicles"
