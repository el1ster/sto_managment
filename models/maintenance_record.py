from peewee import (
    Model,
    ForeignKeyField,
    DateField,
    IntegerField,
    DecimalField,
    CharField,
    TextField
)
from models.db import db
from models.vehicle import Vehicle
from models.employee import Employee
from models.tax_group import TaxGroup

MAINTENANCE_STATUSES = ["new", "in progress", "completed"]


class MaintenanceRecord(Model):
    """
    Запис обслуговування транспортного засобу.

    Args:
        vehicle (Vehicle): Транспортний засіб, який обслуговується.
        service_date (date): Дата виконання обслуговування.
        mileage (int): Поточний пробіг під час обслуговування.
        employee (Employee): Відповідальний працівник.
        material_cost (Decimal): Вартість використаних матеріалів.
        service_type (str): Тип виконаної послуги.
        service_desc (str): Додатковий опис або примітки (необов’язково).
        tax_group (TaxGroup): Група податків, що застосовується (необов’язково).

    Returns:
        MaintenanceRecord: Об'єкт запису обслуговування.

    Raises:
        peewee.IntegrityError: У разі порушення цілісності зовнішніх ключів.
    """
    vehicle: Vehicle = ForeignKeyField(
        Vehicle,
        backref="maintenance_records",
        column_name="vehicle_id",
        null=False
    )

    service_date: DateField = DateField(null=False)

    mileage: int = IntegerField(null=False)

    employee: Employee = ForeignKeyField(
        Employee,
        backref="services",
        column_name="employee_id",
        null=False
    )

    material_cost: DecimalField = DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False
    )

    service_type: str = CharField(max_length=100, null=False)

    service_desc: str = TextField(null=True)

    tax_group: TaxGroup = ForeignKeyField(
        TaxGroup,
        backref="maintenance_records",
        column_name="tax_group_id",
        null=True
    )

    status: str = CharField(
        max_length=20,
        default="new",
        constraints=[]  # опціонально: можна обмежити через CHECK (якщо хочеш)
    )

    class Meta:
        database = db
        table_name = "maintenance_records"
