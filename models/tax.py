from peewee import *
from .db import db


class Tax(Model):
    """
    Податок.

    Args:
        tax_name (str): Назва податку.
        tax_type (str): Тип (напр. 'державний').
        rate (Decimal): Ставка (у відсотках або фіксована).
        is_percent (bool): Чи ставка є відсотковою.
        applies_to (str): До чого застосовується ('зарплата', 'транспорт').
        is_active (bool): Чи активний.
    """
    tax_name = CharField(max_length=100)
    tax_type = CharField(max_length=50)
    rate = DecimalField(max_digits=10, decimal_places=2)
    is_percent = BooleanField(default=True)
    applies_to = CharField(max_length=50)
    is_active = BooleanField(default=True)
    payer = CharField(max_length=20, default='employer')  # приклад

    class Meta:
        database = db
        table_name = "taxes"
