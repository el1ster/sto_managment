from peewee import fn
from models.task import Task
from models.optimization_worker import OptimizationWorker
from models.employee import Employee


def recalculate_workload(employee: Employee) -> None:
    """
    Перераховує поточне навантаження для працівника на основі активних задач.

    Args:
        employee (Employee): Працівник, для якого оновлюється workload.
    """
    total = (Task
             .select(fn.SUM(Task.time_required))
             .where(
                 (Task.assigned_worker == employee) &
                 (Task.status == "in progress")
             )
             .scalar()) or 0.0

    opt_worker = OptimizationWorker.get_or_none(OptimizationWorker.employee == employee)
    if opt_worker:
        opt_worker.workload = total
        opt_worker.save()
