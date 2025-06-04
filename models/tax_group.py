from peewee import Model, AutoField, CharField
from models.db import db


class TaxGroup(Model):
    """
    Група податків, яка об'єднує декілька податкових елементів.

    Args:
        group_id (int): Унікальний ідентифікатор групи (автоінкремент).
        group_name (str): Назва групи податків (унікальна).

    Returns:
        TaxGroup: Об'єкт групи податків.

    Raises:
        peewee.IntegrityError: Якщо вказано неунікальну назву групи.
    """
    group_id: int = AutoField(primary_key=True)

    group_name: str = CharField(max_length=100, unique=True)

    class Meta:
        database = db
        table_name = "tax_groups"
