from datetime import datetime
from typing import Tuple
import pandas as pd
import numpy as np
from statsforecast import StatsForecast
from statsforecast.models import AutoETS
from logic.forecast_utils import get_monthly_coefficients


def prepare_forecast_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Підготовка DataFrame у формат для StatsForecast.

    Args:
        df (pd.DataFrame): Дані з колонками ['ds', 'y'].

    Returns:
        pd.DataFrame: Форматовані дані ['unique_id', 'ds', 'y'].
    """
    df = df.copy()
    df = df.sort_values("ds")
    df["unique_id"] = "expenses"
    df["y"] = df["y"].astype(float)
    return df[["unique_id", "ds", "y"]]


def generate_forecast(
        df: pd.DataFrame,
        horizon: int,
        start_train_date: datetime,
        start_forecast_date: datetime,
        apply_seasonality: bool = False
) -> pd.DataFrame:
    """
    Генерує покроковий прогноз витрат із опціональною сезонністю.

    Args:
        df (pd.DataFrame): Історичні дані ['ds', 'y'].
        horizon (int): Горизонт прогнозування (у місяцях).
        start_train_date (datetime): Початок навчального періоду.
        start_forecast_date (datetime): Перша дата прогнозу.
        apply_seasonality (bool): Чи застосовувати зовнішні сезонні коефіцієнти.

    Returns:
        pd.DataFrame: Результати ['ds', 'y', 'adjusted_y'].
    """
    df = df.copy()
    df["y"] = df["y"].astype(float)
    df = df.sort_values("ds").reset_index(drop=True)

    train_df = df[
        (df["ds"] >= pd.to_datetime(start_train_date)) &
        (df["ds"] < pd.to_datetime(start_forecast_date))
        ].copy()

    if len(train_df) < 3:
        raise ValueError("Недостатньо даних у навчальному періоді.")

    seasonal_coeffs = get_monthly_coefficients(df, column="y") if apply_seasonality else {}

    forecasts = []
    current_df = train_df.copy()

    for i in range(horizon):
        forecast_date = start_forecast_date + pd.DateOffset(months=i)

        model_input = prepare_forecast_dataframe(current_df)
        model = StatsForecast(models=[AutoETS()], freq="MS")
        model.fit(model_input)

        prediction = model.predict(h=1)
        y_pred = float(prediction["AutoETS"].iloc[0])

        if apply_seasonality:
            month = forecast_date.month
            adjusted_y = y_pred * seasonal_coeffs.get(month, 1.0)
        else:
            adjusted_y = y_pred

        forecasts.append({
            "ds": forecast_date,
            "y": y_pred,
            "adjusted_y": adjusted_y
        })

        current_df = pd.concat([
            current_df,
            pd.DataFrame([{"ds": forecast_date, "y": adjusted_y}])
        ], ignore_index=True)

    result_df = pd.DataFrame(forecasts)
    return result_df
