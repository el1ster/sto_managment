from peewee import Model, CharField, DateField, BooleanField, IntegerField
from models.db import db

class Vehicle(Model):
    """
    Транспортний засіб.

    Args:
        license_plate (str): Номер.
        model (str): Модель.
        year (int): Рік випуску.
        vin (str): VIN-код.
        purchase_date (date): Дата купівлі.
        is_active (bool): Активний/списаний.
    """
    license_plate = CharField(max_length=20, unique=True)
    model = CharField(max_length=100)
    year = IntegerField(null=True)
    vin = CharField(max_length=50, null=True)
    purchase_date = DateField(null=True)
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = "vehicles"
