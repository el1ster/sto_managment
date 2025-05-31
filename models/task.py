from peewee import (
    Model, CharField, FloatField, DateTimeField, IntegerField, ForeignKeyField, BooleanField
)
from models.db import db  # Импортируй свою инициализацию базы данных


class Task(Model):
    """
    Модель завдання (tasks) — з повним відображенням таблиці.

    Fields:
        id (int): Первинний ключ.
        name (str): Назва завдання, не порожня.
        time_required (float): Необхідний час (години).
        status (str): Статус виконання (наприклад, 'pending').
        archived_at (datetime): Дата архівації (не NULL).
        specialization (str): Спеціалізація (наприклад, "електрика").
        in_queue (bool/int): Чи знаходиться в черзі (1 або 0).
        vehicle_id (int): Зв’язок з автомобілем.
        maintenance_id (int): Зв’язок із записом обслуговування.
    """

    name = CharField(max_length=100, null=False)
    time_required = FloatField(null=False)
    status = CharField(max_length=50, default='pending', null=False)
    archived_at = DateTimeField(null=False)  # Якщо поле може бути NULL, додай null=True
    specialization = CharField(max_length=255, null=False)
    in_queue = BooleanField(null=False, default=True)  # Можна і як IntegerField, якщо хочеш 0/1
    vehicle_id = IntegerField(null=False)
    maintenance_id = IntegerField(null=False)

    class Meta:
        database = db
        table_name = "tasks"
