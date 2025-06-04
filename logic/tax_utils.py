from decimal import Decimal
from typing import Union, Tuple
from models.tax_group import TaxGroup
from models.tax_group_item import TaxGroupItem
from models.tax import Tax
from models.salary_record import SalaryRecord
from models.maintenance_record import MaintenanceRecord


def get_tax_breakdown(record: Union[SalaryRecord, MaintenanceRecord]) -> dict[str, Decimal]:
    """
    Обчислює загальний розподіл податків без врахування платника.

    Args:
        record: Об'єкт SalaryRecord або MaintenanceRecord.

    Returns:
        dict[str, Decimal]: Словник із назвами податків і відповідними сумами.
    """
    try:

        if not getattr(record, "tax_group_id", None):
             return {}

        tax_group = record.tax_group
        if not tax_group:
            return {}


        breakdown: dict[str, Decimal] = {}

        if isinstance(record, SalaryRecord):
            base_amount = Decimal(record.base_salary or 0) + Decimal(record.bonus or 0)
        else:
            base_amount = Decimal(record.material_cost or 0)

        query = (
            Tax.select()
            .join(TaxGroupItem, on=(Tax.id == TaxGroupItem.tax))
            .where(TaxGroupItem.group == tax_group)
        )

        for tax in query:
            if not tax.is_active:
                continue

            if tax.is_percent:
                tax_amount = base_amount * Decimal(tax.rate or 0) / Decimal(100)
            else:
                tax_amount = Decimal(tax.rate or 0)

            tax_amount = round(tax_amount, 2)

            breakdown[tax.tax_name] = tax_amount

        return breakdown

    except Exception as e:
        print(f"[ERROR] Tax breakdown error: {e}")
        return {}


def split_tax_breakdown(record: Union[SalaryRecord, MaintenanceRecord]) -> Tuple[
    dict[str, Decimal], dict[str, Decimal]]:
    """
    Розділяє податки за платником: окремо для підприємства та працівника.

    Args:
        record: Об'єкт SalaryRecord або MaintenanceRecord.

    Returns:
        Tuple[dict[str, Decimal], dict[str, Decimal]]:
            Перший словник — податки підприємства (payer='employer'),
            другий — податки працівника (payer='employee').
    """
    employer_taxes: dict[str, Decimal] = {}
    employee_taxes: dict[str, Decimal] = {}

    try:

        if not getattr(record, "tax_group_id", None):
            return employer_taxes, employee_taxes

        tax_group = record.tax_group
        if not tax_group:
            return employer_taxes, employee_taxes

        if isinstance(record, SalaryRecord):
            base_amount = Decimal(record.base_salary or 0) + Decimal(record.bonus or 0)
        else:
            base_amount = Decimal(record.material_cost or 0)

        query = (
            Tax.select()
            .join(TaxGroupItem, on=(Tax.id == TaxGroupItem.tax))
            .where(TaxGroupItem.group == tax_group)
        )

        for tax in query:
            if not tax.is_active:
                continue

            tax_amount = (
                base_amount * Decimal(tax.rate or 0) / Decimal(100)
                if tax.is_percent else Decimal(tax.rate or 0)
            )
            tax_amount = round(tax_amount, 2)

            payer = (tax.payer or "employer").strip().lower()
            if payer == "employee":
                employee_taxes[tax.tax_name] = tax_amount
            else:
                employer_taxes[tax.tax_name] = tax_amount


        return employer_taxes, employee_taxes

    except Exception as e:
        print(f"[ERROR] Помилка при розподілі податків: {e}")
        return employer_taxes, employee_taxes
