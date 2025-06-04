def translate_payer(payer: str) -> str:
    """
    Повертає локалізовану назву платника.

    Args:
        payer (str): Значення з БД ('employer' або 'employee').

    Returns:
        str: Перекладене значення ('підприємство', 'працівник').
    """
    return {
        "employer": "підприємство",
        "employee": "працівник"
    }.get(payer, payer)  # якщо невідоме значення — повертаємо як є
