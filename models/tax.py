from peewee import (
    Model,
    CharField,
    DecimalField,
    BooleanField
)
from models.db import db


class Tax(Model):
    """
    Податок, що застосовується до операцій у системі.

    Args:
        tax_name (str): Назва податку.
        tax_type (str): Тип податку (наприклад, "державний", "місцевий").
        rate (Decimal): Ставка податку — відсоткова або фіксована.
        is_percent (bool): Ознака, чи ставка є відсотковою.
        applies_to (str): Сфера застосування (наприклад, "зарплата", "транспорт").
        payer (str): Хто сплачує податок (наприклад, "employer", "employee").
        is_active (bool): Чи активний податок.

    Returns:
        Tax: Об'єкт податку.

    Raises:
        peewee.IntegrityError: У разі спроби збереження невалідного запису.
    """
    tax_name = CharField(max_length=100, unique=True)
    tax_type = CharField(max_length=50, null=False)
    rate = DecimalField(max_digits=10, decimal_places=2, null=False)
    is_percent = BooleanField(default=True, null=False)
    applies_to = CharField(max_length=50, null=False)
    payer = CharField(max_length=20, default="employer", null=False)
    is_active = BooleanField(default=True, null=False)

    class Meta:
        database = db
        table_name = "taxes"
