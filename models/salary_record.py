from peewee import (
    Model,
    ForeignKeyField,
    DateField,
    DecimalField,
    TextField
)
from models.db import db
from models.employee import Employee
from models.tax_group import TaxGroup
from decimal import Decimal


class SalaryRecord(Model):
    """
    Запис нарахування заробітної плати працівнику.

    Args:
        employee (Employee): Працівник, якому здійснено виплату.
        salary_month (date): Місяць, за який нараховано зарплату.
        base_salary (Decimal): Основна заробітна плата.
        bonus (Decimal): Сума бонусу (премії).
        total_payout (Decimal): Загальна сума виплати.
        comment (str): Додаткові примітки (необов’язково).

    Returns:
        SalaryRecord: Об'єкт запису зарплати.

    Raises:
        peewee.IntegrityError: Якщо відсутній зв'язаний працівник.
    """
    employee: Employee = ForeignKeyField(
        Employee,
        backref="salary_records",
        column_name="employee_id",
        null=False
    )
    salary_month: DateField = DateField(null=False)
    base_salary: DecimalField = DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False
    )
    bonus: DecimalField = DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tax_group: TaxGroup = ForeignKeyField(
        TaxGroup,
        backref="salary_records",
        column_name="tax_group_id",
        null=True  # дозволяє залишити пустим, якщо ще не заповнено
    )
    comment: str = TextField(null=True)

    class Meta:
        database = db
        table_name = "salary_records"
