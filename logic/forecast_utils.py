import pandas as pd


def get_monthly_coefficients(df: pd.DataFrame, column: str) -> dict[int, float]:
    """
    Обчислює сезонні коефіцієнти для кожного місяця на основі середнього значення за колонкою.

    Args:
        df (pd.DataFrame): DataFrame з колонками 'ds' (дата) та цільовим числовим стовпцем.
        column (str): Назва числової колонки для аналізу.

    Returns:
        dict[int, float]: Коефіцієнти у форматі {номер_місяця: коефіцієнт}.
    """
    df = df.copy()
    df["month"] = df["ds"].dt.month

    monthly_avg = df.groupby("month")[column].mean()
    overall_avg = df[column].mean()

    coefficients = {
        month: round(monthly_avg[month] / overall_avg, 4) if overall_avg else 1.0
        for month in monthly_avg.index
    }

    return coefficients
