from peewee import fn
from datetime import date, timedelta
from collections import defaultdict
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from logic.forecast_utils import get_group_tax_total
from models.maintenance_record import MaintenanceRecord
from models.salary_record import SalaryRecord
from models.tax_group_item import TaxGroupItem
from models.vehicle import Vehicle
from models.employee import Employee



def get_vehicle_forecast(vehicle_id: int, months: int = 3) -> dict:
    end_date = date.today().replace(day=1)
    start_date = end_date - timedelta(days=365)

    query = (MaintenanceRecord
             .select(
        fn.DATE_FORMAT(MaintenanceRecord.service_date, '%Y-%m').alias('month'),
        fn.SUM(MaintenanceRecord.material_cost).alias('materials'),
        MaintenanceRecord.tax_group)
             .where(
        (MaintenanceRecord.vehicle == vehicle_id) &
        (MaintenanceRecord.service_date >= start_date))
             .group_by(fn.DATE_FORMAT(MaintenanceRecord.service_date, '%Y-%m'), MaintenanceRecord.tax_group)
             .dicts())

    stats = defaultdict(lambda: {'materials': 0.0, 'tax': 0.0})

    for row in query:
        month = row['month']
        materials = float(row['materials'] or 0)
        group_id = row['tax_group'] if isinstance(row['tax_group'], int) else (
            row['tax_group'].id if row['tax_group'] else None)

        stats[month]['materials'] += materials
        stats[month]['tax'] += get_group_tax_total(group_id, materials, payer_filter='employer')

    def forecast(series):
        if len(series) < 2:
            return [sum(series) / len(series) if series else 0.0] * months
        model = ExponentialSmoothing(series, trend='add', seasonal=None)
        fit = model.fit()
        return fit.forecast(months)

    sorted_months = sorted(stats.keys())
    material_series = [stats[m]['materials'] for m in sorted_months]
    tax_series = [stats[m]['tax'] for m in sorted_months]

    return {
        "materials": round(sum(forecast(material_series)), 2),
        "taxes": round(sum(forecast(tax_series)), 2),
    }


def get_summary_statistics(start_date: date, end_date: date) -> dict:
    transport_cost = 0.0
    transport_tax = 0.0

    services = (MaintenanceRecord
                .select(
        fn.SUM(MaintenanceRecord.material_cost).alias('materials'),
        MaintenanceRecord.tax_group)
                .where(MaintenanceRecord.service_date.between(start_date, end_date))
                .group_by(MaintenanceRecord.tax_group))

    for row in services.dicts():
        materials = float(row['materials'] or 0)
        transport_cost += materials
        transport_tax += get_group_tax_total(row['tax_group'], materials, payer_filter='employer')

    employee_cost = 0.0
    employee_tax = 0.0

    payrolls = (SalaryRecord
                .select(fn.SUM(SalaryRecord.base_salary + SalaryRecord.bonus).alias('total'),
                        SalaryRecord.tax_group)
                .where(SalaryRecord.salary_month.between(start_date, end_date))
                .group_by(SalaryRecord.tax_group))

    for row in payrolls.dicts():
        base = float(row['total'] or 0)
        employee_cost += base
        employee_tax += get_group_tax_total(row['tax_group'], base, payer_filter='employer')

    return {
        "Транспорт": round(transport_cost, 2),
        "Працівники": round(employee_cost, 2),
        "Податки": round(transport_tax + employee_tax, 2),
        "Разом": round(transport_cost + employee_cost + transport_tax + employee_tax, 2)
    }


def get_vehicle_breakdown(start_date: date, end_date: date):
    # print(f"[DEBUG] get_vehicle_breakdown called with range: {start_date} to {end_date}")

    try:
        records = (MaintenanceRecord
                   .select(
            Vehicle.id,
            Vehicle.number_plate,
            fn.SUM(MaintenanceRecord.material_cost).alias('materials'),
            MaintenanceRecord.tax_group)
                   .join(Vehicle)
                   .where(MaintenanceRecord.service_date.between(start_date, end_date))
                   .group_by(Vehicle.id, Vehicle.number_plate, MaintenanceRecord.tax_group))

        result = []
        for row in records.dicts():
            # print(f"[DEBUG] Raw row: {row}")
            materials = float(row['materials'] or 0)
            tax = get_group_tax_total(row['tax_group'], materials, payer_filter='employer')
            total = round(materials + tax, 2)

            result.append({
                "id": row['id'],
                "name": row['number_plate'],
                "breakdown": {
                    "materials": materials,
                    "taxes": tax
                },
                "total": total
            })
            # print(f"[DEBUG] Added vehicle: id={row['id']}, name={row['number_plate']}, total={total}")

        return result

    except Exception as e:
        # print(f"[ERROR] get_vehicle_breakdown failed: {e}")
        return []


def get_employee_breakdown(start_date: date, end_date: date):
    # print(f"[DEBUG] get_employee_breakdown called with range: {start_date} to {end_date}")

    try:
        records = (SalaryRecord
                   .select(
            Employee.id,
            Employee.full_name,
            fn.SUM(SalaryRecord.base_salary).alias('base'),
            fn.SUM(SalaryRecord.bonus).alias('bonus'),
            SalaryRecord.tax_group)
                   .join(Employee)
                   .where(SalaryRecord.salary_month.between(start_date, end_date))
                   .group_by(Employee.id, Employee.full_name, SalaryRecord.tax_group))

        result = []

        for row in records.dicts():
            # print(f"[DEBUG] Raw employee row: {row}")
            base = float(row['base'] or 0)
            bonus = float(row['bonus'] or 0)
            total_income = base + bonus
            tax = get_group_tax_total(row['tax_group'], total_income, payer_filter='employer')
            total = round(total_income + tax, 2)

            result.append({
                "id": row['id'],
                "name": row['full_name'],
                "breakdown": {
                    "base": base,
                    "bonus": bonus,
                    "taxes": tax
                },
                "total": total
            })

            # print(f"[DEBUG] Added employee: id={row['id']}, name={row['full_name']}, total={total}")

        return result

    except Exception as e:
        # print(f"[ERROR] get_employee_breakdown failed: {e}")
        return []


def get_employee_monthly_breakdown(employee_id: int, month: str) -> dict:
    # print(f"[DEBUG] get_employee_monthly_breakdown called with employee_id={employee_id}, month={month}")

    start_date = date.fromisoformat(f'{month}-01')
    end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    # print(f"[DEBUG] Date range: {start_date} to {end_date}")

    record = (SalaryRecord
              .select(
        fn.SUM(SalaryRecord.base_salary).alias('base'),
        fn.SUM(SalaryRecord.bonus).alias('bonus'),
        SalaryRecord.tax_group)
              .where(
        (SalaryRecord.employee == employee_id) &
        (SalaryRecord.salary_month >= start_date) &
        (SalaryRecord.salary_month < end_date))
              .group_by(SalaryRecord.tax_group)
              .dicts()
              .first())

    # print(f"[DEBUG] Raw record: {record}")

    if not record:
        # print("[DEBUG] No records found, returning zeros")
        return {'base': 0.0, 'bonus': 0.0, 'taxes': 0.0, 'total': 0.0}

    base = float(record.get('base') or 0)
    bonus = float(record.get('bonus') or 0)
    tax_group = record.get('tax_group')
    group_id = tax_group.get('id') if isinstance(tax_group, dict) else tax_group

    # print(f"[DEBUG] Calculated base={base}, bonus={bonus}, group_id={group_id}")

    tax = get_group_tax_total(group_id, base + bonus, payer_filter='employer')
    total = round(base + bonus + tax, 2)

    # print(f"[DEBUG] Calculated tax={tax}, total={total}")

    return {
        'base': base,
        'bonus': bonus,
        'taxes': tax,
        'total': total
    }


def get_vehicle_monthly_breakdown(vehicle_id: int, month: str) -> dict:
    # print(f"[DEBUG] get_vehicle_monthly_breakdown called with vehicle_id={vehicle_id}, month={month}")

    start_date = date.fromisoformat(f'{month}-01')
    end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    # print(f"[DEBUG] Date range: {start_date} to {end_date}")

    record = (MaintenanceRecord
              .select(
        fn.SUM(MaintenanceRecord.material_cost).alias('materials'),
        MaintenanceRecord.tax_group)
              .where(
        (MaintenanceRecord.vehicle == vehicle_id) &
        (MaintenanceRecord.service_date >= start_date) &
        (MaintenanceRecord.service_date < end_date))
              .group_by(MaintenanceRecord.tax_group)
              .dicts()
              .first())

    # print(f"[DEBUG] Raw record: {record}")

    if not record:
        print("[DEBUG] No records found, returning zeros")
        return {'materials': 0.0, 'taxes': 0.0, 'total': 0.0}

    materials = float(record.get('materials') or 0)
    tax_group = record.get('tax_group')
    group_id = tax_group.get('id') if isinstance(tax_group, dict) else tax_group

    # print(f"[DEBUG] materials={materials}, group_id={group_id}")

    tax = get_group_tax_total(group_id, materials, payer_filter='employer')
    total = round(materials + tax, 2)

    # print(f"[DEBUG] Calculated tax={tax}, total={total}")

    return {
        'materials': materials,
        'taxes': tax,
        'total': total
    }


def get_employee_available_months(employee_id: int, start_date: date, end_date: date) -> list:
    # print(f"[DEBUG] get_employee_available_months: id={employee_id}, range=({start_date}, {end_date})")
    query = (SalaryRecord
             .select(fn.DATE_FORMAT(SalaryRecord.salary_month, '%Y-%m').alias('month'))
             .where(
        (SalaryRecord.employee == employee_id) &
        (SalaryRecord.salary_month.between(start_date, end_date))
    )
             .distinct()
             .order_by(fn.DATE_FORMAT(SalaryRecord.salary_month, '%Y-%m')))
    months = [row['month'] for row in query.dicts()]
    # print(f"[DEBUG] -> found months: {months}")
    return months


def get_vehicle_available_months(vehicle_id: int, start_date: date, end_date: date) -> list:
    # print(f"[DEBUG] get_vehicle_available_months: id={vehicle_id}, range=({start_date}, {end_date})")
    query = (MaintenanceRecord
             .select(fn.DATE_FORMAT(MaintenanceRecord.service_date, '%Y-%m').alias('month'))
             .where(
        (MaintenanceRecord.vehicle == vehicle_id) &
        (MaintenanceRecord.service_date.between(start_date, end_date))
    )
             .distinct()
             .order_by(fn.DATE_FORMAT(MaintenanceRecord.service_date, '%Y-%m')))
    months = [row['month'] for row in query.dicts()]
    # print(f"[DEBUG] -> found months: {months}")
    return months


def get_summary_available_months(start_date: date, end_date: date) -> list:
    # print(f"[DEBUG] get_summary_available_months in range ({start_date}, {end_date})")

    query1 = (MaintenanceRecord
              .select(fn.DATE_FORMAT(MaintenanceRecord.service_date, '%Y-%m').alias('month'))
              .where(MaintenanceRecord.service_date.between(start_date, end_date)))

    query2 = (SalaryRecord
              .select(fn.DATE_FORMAT(SalaryRecord.salary_month, '%Y-%m').alias('month'))
              .where(SalaryRecord.salary_month.between(start_date, end_date)))

    months = set(row['month'] for row in query1.dicts()).union(
        row['month'] for row in query2.dicts())

    sorted_months = sorted(months)
    # print(f"[DEBUG] Summary months: {sorted_months}")
    return sorted_months


def get_detailed_summary_by_month(month: str) -> list:
    try:
        # print(f"[DEBUG] get_detailed_summary_by_month: {month}")
        start_date = date.fromisoformat(f"{month}-01")
        end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)

        transport_materials = 0.0
        transport_tax = 0.0
        transport_breakdown = {"ЕКО": 0.0}

        employee_base = employee_bonus = 0.0
        employee_tax_total = employer_tax_total = 0.0
        employer_tax_breakdown = {"ЄСВ": 0.0, "ЕКО": 0.0}
        employee_tax_breakdown = {"ПДФО": 0.0, "ВЗ": 0.0, "ЄСВ": 0.0}

        # Транспорт
        transport_query = (MaintenanceRecord
                           .select(
            fn.SUM(MaintenanceRecord.material_cost).alias('materials'),
            MaintenanceRecord.tax_group)
                           .where(MaintenanceRecord.service_date.between(start_date, end_date))
                           .group_by(MaintenanceRecord.tax_group)
                           .dicts())

        for row in transport_query:
            materials = float(row['materials'] or 0)
            transport_materials += materials
            group_id = row['tax_group']

            for item in TaxGroupItem.select().where(TaxGroupItem.group_id == group_id):
                tax = item.tax
                if not tax.active or tax.payer != "employer" or tax.applies_to != "транспорт":
                    continue

                if tax.is_percent:
                    val = materials * float(tax.rate) / 100
                else:
                    count = (MaintenanceRecord
                             .select()
                             .where((MaintenanceRecord.service_date.between(start_date, end_date)) &
                                    (MaintenanceRecord.tax_group == group_id))
                             .count())
                    val = float(tax.rate) * count

                transport_tax += val
                name = tax.tax_name.strip().upper()
                if "ЕКО" in name:
                    transport_breakdown["ЕКО"] += val

        # Працівники
        payroll_query = (SalaryRecord
                         .select(
            fn.SUM(SalaryRecord.base_salary).alias('base'),
            fn.SUM(SalaryRecord.bonus).alias('bonus'),
            SalaryRecord.tax_group)
                         .where(SalaryRecord.salary_month.between(start_date, end_date))
                         .group_by(SalaryRecord.tax_group)
                         .dicts())

        for row in payroll_query:
            base = float(row['base'] or 0)
            bonus = float(row['bonus'] or 0)
            total = base + bonus
            employee_base += base
            employee_bonus += bonus
            group_id = row['tax_group']

            for item in TaxGroupItem.select().where(TaxGroupItem.group_id == group_id):
                tax = item.tax
                if not tax.active or tax.applies_to != "зарплата":
                    continue

                val = total * float(tax.rate) / 100 if tax.is_percent else float(tax.rate)
                name = tax.tax_name.strip().upper()

                if tax.payer == "employer":
                    employer_tax_total += val
                    if "ЄСВ" in name:
                        employer_tax_breakdown["ЄСВ"] += val
                    elif "ЕКО" in name:
                        employer_tax_breakdown["ЕКО"] += val

                elif tax.payer == "employee":
                    employee_tax_total += val
                    if "ПДФО" in name:
                        employee_tax_breakdown["ПДФО"] += val
                    elif "ВЗ" in name:
                        employee_tax_breakdown["ВЗ"] += val
                    elif "ЄСВ" in name:
                        employee_tax_breakdown["ЄСВ"] += val

        total_sum = round(
            transport_materials + transport_tax +
            employee_base + employee_bonus + employer_tax_total, 2
        )

        result = [
            ("Транспорт", "Матеріали", transport_materials),
            ("Транспорт", "Податки", transport_tax),

            ("Працівники", "ЗП", employee_base + employee_bonus),
            ("Працівники", "Податки (підприємства)", employer_tax_total),
            ("Працівники", "Податки (працівника)", employee_tax_total),

            ("Податки (підприємство)", "ЄСВ", employer_tax_breakdown["ЄСВ"]),
            ("Податки (підприємство)", "ЕКО", transport_breakdown["ЕКО"]),

            ("Податки (працівник)", "ПДФО", employee_tax_breakdown["ПДФО"]),
            ("Податки (працівник)", "ВЗ", employee_tax_breakdown["ВЗ"]),
            ("Податки (працівник)", "ЄСВ", employee_tax_breakdown["ЄСВ"]),

            ("Сумма", "----------", total_sum)
        ]
        # print("ResM:", result)
        return result
    except Exception as e:
        # print(f"[get_detailed_summary_by_month] Помилка: {e}")
        return []


def get_detailed_summary_by_range(start_date: date, end_date: date) -> list:
    try:
        # print(f"[DEBUG] get_detailed_summary_by_range: {start_date} → {end_date}")

        transport_materials = 0.0
        transport_tax = 0.0
        transport_breakdown = {'ЕКО': 0.0}

        transport_query = (MaintenanceRecord
                           .select(
            fn.SUM(MaintenanceRecord.material_cost).alias('materials'),
            MaintenanceRecord.tax_group)
                           .where(MaintenanceRecord.service_date.between(start_date, end_date))
                           .group_by(MaintenanceRecord.tax_group)
                           .dicts())

        for row in transport_query:
            materials = float(row['materials'] or 0)
            transport_materials += materials
            group_id = row['tax_group']

            for item in TaxGroupItem.select().where(TaxGroupItem.group_id == group_id):
                tax = item.tax
                if not tax.active or tax.payer != 'employer' or tax.applies_to != 'транспорт':
                    continue

                if tax.is_percent:
                    val = materials * float(tax.rate) / 100
                else:
                    count = (MaintenanceRecord
                             .select()
                             .where((MaintenanceRecord.service_date.between(start_date, end_date)) &
                                    (MaintenanceRecord.tax_group == group_id))
                             .count())
                    val = float(tax.rate) * count

                transport_tax += val
                name = tax.tax_name.strip().upper()
                if 'ЕКО' in name:
                    transport_breakdown['ЕКО'] += val

        employee_base = 0.0
        employee_bonus = 0.0
        employee_tax_total = 0.0
        employer_tax_total = 0.0

        employer_tax_breakdown = {'ЄСВ': 0.0, 'ЕКО': 0.0}
        employee_tax_breakdown = {'ПДФО': 0.0, 'ВЗ': 0.0}

        payroll_query = (SalaryRecord
                         .select(
            fn.SUM(SalaryRecord.base_salary).alias('base'),
            fn.SUM(SalaryRecord.bonus).alias('bonus'),
            SalaryRecord.tax_group)
                         .where(SalaryRecord.salary_month.between(start_date, end_date))
                         .group_by(SalaryRecord.tax_group)
                         .dicts())

        for row in payroll_query:
            base = float(row['base'] or 0)
            bonus = float(row['bonus'] or 0)
            total = base + bonus
            employee_base += base
            employee_bonus += bonus
            group_id = row['tax_group']

            for item in TaxGroupItem.select().where(TaxGroupItem.group_id == group_id):
                tax = item.tax
                if not tax.active or tax.applies_to != 'зарплата':
                    continue

                val = total * float(tax.rate) / 100 if tax.is_percent else float(tax.rate)
                name = tax.tax_name.strip().upper()

                if tax.payer == 'employer':
                    employer_tax_total += val
                    if 'ЄСВ' in name:
                        employer_tax_breakdown['ЄСВ'] += val

                elif tax.payer == 'employee':
                    employee_tax_total += val
                    if 'ПДФО' in name:
                        employee_tax_breakdown['ПДФО'] += val
                    elif 'ВЗ' in name:
                        employee_tax_breakdown['ВЗ'] += val
                    elif 'ЄСВ' in name:
                        employee_tax_breakdown['ЄСВ'] += val

        total_sum = round(
            transport_materials + transport_tax +
            employee_base + employee_bonus +
            employer_tax_total + employee_tax_total, 2
        )

        result = [
            ("Транспорт", "Матеріали", transport_materials),
            ("Транспорт", "Податки", transport_tax),

            ("Працівники", "ЗП", employee_base + employee_bonus),
            ("Працівники", "Податки (підприємство)", employer_tax_total),
            ("Працівники", "Податки (працівник)", employee_tax_total),

            ("Податки (підприємство)", "ЄСВ", employer_tax_breakdown['ЄСВ']),
            ("Податки (підприємство)", "ЕКО", transport_breakdown['ЕКО']),

            ("Податки (працівник)", "ПДФО", employee_tax_breakdown['ПДФО']),
            ("Податки (працівник)", "ВЗ", employee_tax_breakdown['ВЗ']),

            ("Разом", "", total_sum)
        ]

        # print(result)
        return result

    except Exception as e:
        # print(f"[get_detailed_summary_by_range] Помилка: {e}")
        return []
