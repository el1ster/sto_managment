from peewee import *
from .db import db
from .tax import Tax
from .tax_group import TaxGroup


class TaxGroupItem(Model):
    """
    Прив’язка податку до групи.

    Args:
        group (TaxGroup): FK на групу.
        tax (Tax): FK на податок.
    """
    group = ForeignKeyField(TaxGroup, backref="items", column_name="group_id")
    tax = ForeignKeyField(Tax, backref="group_items", column_name="tax_id")

    class Meta:
        database = db
        table_name = "tax_group_items"
        primary_key = CompositeKey('group', 'tax')
