from peewee import *
from .db import db
from .vehicle import Vehicle
from .employee import Employee
from .tax_group import TaxGroup


class MaintenanceRecord(Model):
    """
    Запис обслуговування транспортного засобу.

    Args:
        vehicle (Vehicle): FK на транспорт.
        service_date (date): Дата обслуговування.
        mileage (int): Пробіг.
        employee (Employee): Відповідальний працівник.
        material_cost (Decimal): Вартість матеріалів.
        service_type (str): Тип послуги.
        service_desc (str): Примітка/опис.
        tax_group (TaxGroup): Група податків.
    """
    vehicle = ForeignKeyField(Vehicle, backref="maintenance_records", column_name="vehicle_id")
    service_date = DateField()
    mileage = IntegerField()
    employee = ForeignKeyField(Employee, backref="services", column_name="employee_id")
    material_cost = DecimalField(max_digits=10, decimal_places=2)
    service_type = CharField(max_length=100)
    service_desc = TextField(null=True)
    tax_group = ForeignKeyField(TaxGroup, backref="maintenance_records", column_name="tax_group_id", null=True)

    class Meta:
        database = db
        table_name = "maintenance_records"
