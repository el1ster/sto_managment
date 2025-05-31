import logging
from datetime import date
import pandas as pd
import numpy as np
from peewee import fn
from models.tax import Tax
from models.tax_group import TaxGroup
from models.tax_group_item import TaxGroupItem

from typing import Literal
from statsforecast import StatsForecast
from statsforecast.models import AutoETS

# Лог-файл
logging.basicConfig(filename='../forecast_debug.log', level=logging.INFO, format='[%(asctime)s] %(message)s')


def get_group_tax_total(group_id: int, base: float, payer_filter='employer', applies_to=None) -> float:
    total = 0.0
    if not group_id:
        return 0.0
    for item in TaxGroupItem.select().where(TaxGroupItem.group_id == group_id):
        tax = item.tax
        if not tax.active:
            continue
        if tax.payer != payer_filter:
            continue
        if applies_to and tax.applies_to != applies_to:
            continue
        total += base * float(tax.rate) / 100 if tax.is_percent else float(tax.rate)
    return round(total, 2)


def fetch_monthly_components(start_date: date, end_date: date) -> pd.DataFrame:
    start_date, end_date = start_date.replace(day=1), end_date.replace(day=1)
    months_range = pd.date_range(start_date, end_date, freq="MS")
    data = {m: {'salary': 0.0, 'materials': 0.0, 'taxes': 0.0, 'service_count': 0} for m in months_range}

    transport_q = (
        MaintenanceRecord
        .select(
            fn.DATE_FORMAT(MaintenanceRecord.service_date, "%Y-%m").alias("ym"),
            fn.COUNT(MaintenanceRecord.id).alias("cnt"),
            fn.SUM(MaintenanceRecord.material_cost).alias("materials"),
            MaintenanceRecord.tax_group
        )
        .where(MaintenanceRecord.service_date.between(start_date, end_date))
        .group_by(fn.DATE_FORMAT(MaintenanceRecord.service_date, "%Y-%m"), MaintenanceRecord.tax_group)
        .dicts()
    )
    for row in transport_q:
        ym = pd.Timestamp(f"{row['ym']}-01")
        count = int(row["cnt"] or 0)
        materials = float(row["materials"] or 0)
        tax = get_group_tax_total(row["tax_group"], materials, payer_filter='employer', applies_to='транспорт')
        data[ym]["materials"] += materials
        data[ym]["taxes"] += tax
        data[ym]["service_count"] += count

    salary_q = (
        SalaryRecord
        .select(
            fn.DATE_FORMAT(SalaryRecord.salary_month, "%Y-%m").alias("ym"),
            fn.SUM(SalaryRecord.base_salary + SalaryRecord.bonus).alias("total"),
            SalaryRecord.tax_group
        )
        .where(SalaryRecord.salary_month.between(start_date, end_date))
        .group_by(fn.DATE_FORMAT(SalaryRecord.salary_month, "%Y-%m"), SalaryRecord.tax_group)
        .dicts()
    )
    for row in salary_q:
        ym = pd.Timestamp(f"{row['ym']}-01")
        base = float(row["total"] or 0)
        tax = get_group_tax_total(row["tax_group"], base, payer_filter='employer', applies_to='зарплата')
        data[ym]["salary"] += base
        data[ym]["taxes"] += tax

    df = pd.DataFrame([{"ds": m, **data[m]} for m in months_range]).sort_values("ds")
    df["avg_service_cost"] = df.apply(
        lambda row: row["materials"] / row["service_count"] if row["service_count"] else 0.0,
        axis=1
    )
    logging.info("=== DF_HIST ===\n%s", df.to_string(index=False))
    return df


def get_monthly_coefficients(df: pd.DataFrame, column: str) -> dict:
    df = df.copy()
    df["month"] = df["ds"].dt.month
    monthly_avg = df.groupby("month")[column].mean()
    overall_avg = df[column].mean()
    coefficients = {month: round(monthly_avg[month] / overall_avg, 4) if overall_avg else 1.0 for month in
                    monthly_avg.index}
    logging.info("COEFF %s: %s", column, coefficients)
    return coefficients


def forecast_by_category(
        start_date: date,
        end_date: date,
        horizon: int = 6,
        fill_strategy: Literal["zero", "nan"] = "nan",
        add_noise: bool = False,
) -> pd.DataFrame:
    # add_noise = True
    df_hist = fetch_monthly_components(start_date, end_date)
    if (df_hist["salary"].sum() == 0) and (df_hist["materials"].sum() == 0) and (df_hist["taxes"].sum() == 0):
        raise ValueError("Історичних даних для прогнозу у вказаному діапазоні немає.")

    salary_coeff = get_monthly_coefficients(df_hist, "salary")
    materials_coeff = get_monthly_coefficients(df_hist, "materials")

    result_df = pd.DataFrame({
        "ds": pd.date_range(
            start=pd.to_datetime(end_date).replace(day=1) + pd.DateOffset(months=1),
            periods=horizon,
            freq="MS"
        )
    })

    def forecast_column(col_name: str) -> np.ndarray:
        tmp = df_hist[["ds", col_name]].copy()
        tmp[col_name] = tmp[col_name].round(-2)  # округление до сотен
        tmp = tmp.rename(columns={col_name: "y"})
        tmp["unique_id"] = col_name
        if fill_strategy == "zero":
            tmp["y"].fillna(0, inplace=True)

        sf = StatsForecast(models=[AutoETS(season_length=12, model="ZZZ")], freq="MS")
        fc = sf.forecast(df=tmp[["unique_id", "ds", "y"]], h=horizon)
        values = fc["AutoETS"].values
        logging.info("FORECAST %s: %s", col_name, values)
        return values

    def maybe_add_noise(array: np.ndarray) -> np.ndarray:
        if not add_noise:
            return array
        noise = np.random.normal(loc=1.0, scale=0.0025, size=len(array))
        return array * noise

    forecast_salary = maybe_add_noise(forecast_column("salary"))
    forecast_materials = maybe_add_noise(forecast_column("materials"))
    forecast_services = forecast_column("service_count")

    result_df["salary"] = forecast_salary
    result_df["materials"] = forecast_materials
    result_df["service_count"] = np.round(forecast_services).astype(int)

    result_df["month"] = result_df["ds"].dt.month
    result_df["salary"] *= result_df["month"].map(salary_coeff)
    result_df["materials"] *= result_df["month"].map(materials_coeff)

    result_df["salary"] = result_df["salary"].round(-1)
    result_df["materials"] = result_df["materials"].round(-1)

    result_df["taxes"] = (result_df["salary"].round(-1) * 0.22) + (result_df["service_count"] * 150)
    result_df["taxes"] = result_df["taxes"].round(0)

    result_df["total"] = (result_df["salary"] + result_df["materials"] + result_df["taxes"]).round(0)
    result_df.drop(columns=["month"], inplace=True)

    logging.info("=== RESULT ===\n%s", result_df.to_string(index=False))
    return result_df
