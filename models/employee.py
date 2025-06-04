from peewee import (
    Model,
    CharField,
    ForeignKeyField,
    DateField,
    BooleanField,
    DateTimeField
)
from models.db import db
from models.employee_position import EmployeePosition
from models.user import User  # Потрібен для ForeignKeyField


class Employee(Model):
    """
    Працівник сервісної станції.

    Args:
        full_name (str): Повне ім’я працівника.
        phone (str): Номер телефону (необов’язковий).
        email (str): Електронна пошта (необов’язкова).
        hire_date (date): Дата прийому на роботу.
        position (EmployeePosition): Посада працівника (зовнішній ключ).
        user (User): Прив’язаний обліковий запис користувача (необов’язково).
        last_login (datetime): Дата та час останнього входу саме цього працівника.
        is_active (bool): Ознака активності працівника.

    Returns:
        Employee: Об'єкт працівника.

    Raises:
        peewee.IntegrityError: У разі порушення цілісності зв’язків.
    """

    full_name: str = CharField(max_length=100)

    phone: str = CharField(max_length=20, null=True)

    email: str = CharField(max_length=100, null=True)

    hire_date: DateField = DateField(null=True)

    position: EmployeePosition = ForeignKeyField(
        EmployeePosition,
        backref="employees",
        column_name="position_id"
    )

    user: User = ForeignKeyField(
        User,
        backref="employees",
        column_name="user_id",
        null=True
    )

    last_login: DateTimeField = DateTimeField(null=True)

    is_active: bool = BooleanField(default=True)

    class Meta:
        database = db
        table_name = "employees"
