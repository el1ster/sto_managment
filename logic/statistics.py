from typing import Dict
import pandas as pd
import numpy as np
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
from sklearn.metrics import mean_absolute_error


def get_overall_forecast_with_accuracy(
    df: pd.DataFrame,
    horizon: int = 6,
    used_months: int = 12
) -> Dict:
    """
    Прогнозує загальні витрати на основі DataFrame і повертає прогноз та точність.

    Args:
        df (pd.DataFrame): Історичні дані у форматі (ds: дата, y: значення).
        horizon (int): Кількість місяців для прогнозу.
        used_months (int): Кількість останніх місяців для тренування.

    Returns:
        dict: {
            "forecast": {місяць: сума},
            "accuracy_percent": float
        }
    """
    df = df.sort_values("ds")

    if len(df) < used_months + horizon:
        raise ValueError("Недостатньо історичних даних для побудови точного прогнозу.")

    train = df.iloc[:used_months]
    test = df.iloc[used_months:used_months + horizon]

    train_df = train.copy()
    train_df["unique_id"] = "forecast"

    sf = StatsForecast(models=[AutoARIMA()], freq="MS")
    sf.fit(train_df[["unique_id", "ds", "y"]])
    fc = sf.predict(h=horizon)

    y_true = test["y"].values if not test.empty else None
    y_pred = fc["AutoARIMA"].values

    accuracy = 0.0
    if y_true is not None and len(y_true) == len(y_pred):
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        accuracy = round(100 - mape, 2)

    forecast = {
        pd.to_datetime(df["ds"].iloc[-1] + pd.DateOffset(months=i + 1)).strftime("%Y-%m"): float(val)
        for i, val in enumerate(y_pred)
    }

    return {
        "forecast": forecast,
        "accuracy_percent": accuracy
    }
