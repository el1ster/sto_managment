from peewee import *
from .db import db
from .employee import Employee


class SalaryRecord(Model):
    """
    Запис нарахування заробітної плати.

    Args:
        employee (Employee): Працівник.
        salary_month (date): Місяць виплати.
        base_salary (Decimal): Основна зарплата.
        bonus (Decimal): Бонус.
        total_payout (Decimal): Загальна сума виплати.
        comment (str): Примітка.
    """
    employee = ForeignKeyField(Employee, backref="salary_records", column_name="employee_id")
    salary_month = DateField()
    base_salary = DecimalField(max_digits=10, decimal_places=2)
    bonus = DecimalField(max_digits=10, decimal_places=2)
    total_payout = DecimalField(max_digits=10, decimal_places=2)
    comment = TextField(null=True)

    class Meta:
        database = db
        table_name = "salary_records"
