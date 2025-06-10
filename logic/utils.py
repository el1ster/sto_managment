def format_amount(value: float) -> str:
    """
    Форматує число у формат з пробілами між розрядами тисяч.

    Args:
        value (float): Числове значення.

    Returns:
        str: Відформатований рядок, наприклад: '1 024 500.00 грн'
    """
    return f"{value:,.2f} грн".replace(",", " ").replace(".", ".")