from models.tax_group_item import TaxGroupItem


def get_total_cost_with_tax(record) -> float:
    """
    Повертає суму з урахуванням податків (лише employer-податки).

    Args:
        record: SalaryRecord або MaintenanceRecord.

    Returns:
        float: Загальна сума витрат (основа + податки).
    """
    try:
        base_amount = float(
            record.base_salary + record.bonus
            if hasattr(record, 'bonus') else
            record.material_cost
        )

        tax_group = getattr(record, 'tax_group', None)
        if not tax_group:
            return round(base_amount, 2)

        tax_sum = 0.0
        for item in TaxGroupItem.select().where(TaxGroupItem.group == tax_group):
            tax = item.tax
            if not tax.is_active or tax.payer != "employer":
                continue

            if tax.applies_to == "зарплата" and hasattr(record, 'bonus'):
                val = base_amount * float(tax.rate) / 100 if tax.is_percent else float(tax.rate)
            elif tax.applies_to == "транспорт" and not hasattr(record, 'bonus'):
                val = base_amount * float(tax.rate) / 100 if tax.is_percent else float(tax.rate)
            else:
                continue

            tax_sum += val

        return round(base_amount + tax_sum, 2)

    except Exception as e:
        print(f"[ERROR] Tax calc failed: {e}")
        return float(base_amount)
