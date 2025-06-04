from peewee import Model, ForeignKeyField, IntegerField, FloatField, CharField
from models.db import db
from models.employee import Employee


class OptimizationWorker(Model):
    """
    Запис кваліфікації працівника для оптимізації розподілу задач.

    Args:
        employee (Employee): Працівник, що є виконавцем.
        qualification (int): Рівень кваліфікації.
        max_hours (float): Максимальна кількість годин на місяць.
        specialization (str): Спеціалізація.
        workload (float): Поточне навантаження.

    Returns:
        OptimizationWorker: Об'єкт виконавця.
    """

    employee = ForeignKeyField(Employee, backref="optimization_entry", column_name="employee_id", null=False,
                               unique=True)
    qualification = IntegerField(null=True)
    max_hours = FloatField(null=True)
    specialization = CharField(max_length=255, null=True)
    workload = FloatField(null=True)

    class Meta:
        database = db
        table_name = "optimization_workers"
