from pulp import LpProblem, LpMinimize, LpVariable, lpSum
from datetime import date


def optimize_unassigned_tasks(workers: dict, tasks: dict) -> tuple[list[tuple[int, int]], list[int]]:
    """
    Оптимально призначає задачі працівникам з урахуванням дати, навантаження та спеціалізації.

    Args:
        workers (dict): Словник працівників з worker_id -> {
            "specialization": list[str],
            "max_hours": float,
            "workload": float
        }
        tasks (dict): Словник задач з task_id -> {
            "required_specialization": str,
            "time_required": float,
            "created_at": date
        }

    Returns:
        tuple[list[tuple[int, int]], list[int]]: Призначення (worker_id, task_id) та черга task_id.
    """
    prob = LpProblem("TaskAssignmentWithDatePriority", LpMinimize)
    today = date.today()

    # Змінні
    x = LpVariable.dicts("Assignment", [(w, t) for w in workers for t in tasks], cat="Binary")
    queue = LpVariable.dicts("Queue", tasks.keys(), cat="Binary")

    # Розрахунок ваг для задач — старі задачі мають меншу вагу
    weights = {
        t: 1 + (today - tasks[t]["created_at"]).days / 365
        for t in tasks
    }

    # Цільова функція: мінімізуємо сумарне навантаження + штраф за чергу + вагу за дату
    prob += lpSum([
        x[(w, t)] * weights[t] * (workers[w]["workload"] + tasks[t]["time_required"])
        for w in workers for t in tasks
    ]) + lpSum([queue[t] * 1000 for t in tasks])

    # Кожна задача або призначена, або в черзі
    for t in tasks:
        prob += lpSum([x[(w, t)] for w in workers]) + queue[t] == 1

    # Обмеження по годинному ліміту та спеціалізації
    for w in workers:
        prob += lpSum([
            x[(w, t)] * tasks[t]["time_required"]
            for t in tasks
        ]) + workers[w]["workload"] <= workers[w]["max_hours"]

        for t in tasks:
            if tasks[t]["required_specialization"] not in workers[w]["specialization"]:
                prob += x[(w, t)] == 0

    prob.solve()

    # Результати
    assignments = []
    queue_list = []

    for t in tasks:
        if queue[t].value() == 1:
            queue_list.append(t)
        else:
            for w in workers:
                if x[(w, t)].value() == 1:
                    assignments.append((w, t))
                    break

    return assignments, queue_list
