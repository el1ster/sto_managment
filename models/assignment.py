from peewee import Model, ForeignKeyField
from models.db import db
from models.optimization_worker import OptimizationWorker
from models.task import Task


class Assignment(Model):
    """
    Призначення працівника на конкретне завдання.

    Args:
        worker (OptimizationWorker): Об'єкт працівника, призначеного на завдання.
        task (Task): Об'єкт завдання, яке виконується.

    Returns:
        Assignment: Об'єкт призначення працівника на завдання.

    Raises:
        peewee.IntegrityError: Якщо вказано неіснуючий worker або task.
    """
    worker: OptimizationWorker = ForeignKeyField(
        OptimizationWorker,
        backref="assignments",
        column_name="worker_id"
    )

    task: Task = ForeignKeyField(
        Task,
        backref="assignments",
        column_name="task_id"
    )

    class Meta:
        database = db
        table_name = "assignments"
