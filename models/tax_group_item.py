from peewee import Model, ForeignKeyField, CompositeKey
from models.db import db
from models.tax import Tax
from models.tax_group import TaxGroup


class TaxGroupItem(Model):
    """
    Зв’язок між податком і групою податків (багато-до-багатьох).

    Args:
        group (TaxGroup): Група податків, до якої належить податок.
        tax (Tax): Податок, що входить до групи.

    Returns:
        TaxGroupItem: Об'єкт зв’язку між податком і групою.

    Raises:
        peewee.IntegrityError: Якщо зв’язок уже існує або порушено цілісність.
    """
    group: TaxGroup = ForeignKeyField(
        TaxGroup,
        backref="items",
        column_name="group_id"
    )

    tax: Tax = ForeignKeyField(
        Tax,
        backref="group_items",
        column_name="tax_id"
    )

    class Meta:
        database = db
        table_name = "tax_group_items"
        primary_key = CompositeKey("group", "tax")
