# models/forecast_data.py

from peewee import Model, ForeignKeyField, DateField, DecimalField, TimestampField, CharField, TextField
from models.db import db
from models.vehicle import Vehicle


class ForecastData(Model):
    """
    Прогноз обслуговування транспортного засобу.

    Args:
        vehicle (Vehicle): Транспортний засіб, для якого здійснено прогноз.
        predicted_service_date (date): Прогнозована дата обслуговування.
        estimated_cost (Decimal): Орієнтовна вартість.
        created_at (datetime): Дата створення запису.
        model_used (str): Назва моделі прогнозування.
        details (str): Додаткова інформація (опціонально).

    Returns:
        ForecastData: Об'єкт з даними прогнозу.
    """
    vehicle = ForeignKeyField(Vehicle, backref="forecast_data", column_name="vehicle_id", null=False)
    predicted_service_date = DateField(null=True)
    estimated_cost = DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = TimestampField(null=True)
    model_used = CharField(max_length=50, null=True)
    details = TextField(null=True)

    class Meta:
        database = db
        table_name = "forecast_data"
