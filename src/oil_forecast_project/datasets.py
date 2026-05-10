from __future__ import annotations

import numpy as np
import pandas as pd

from oil_forecast_project.analysis.metrics import summarize_errors
from oil_forecast_project.config import PROCESSED_DIR
from oil_forecast_project.data_sources.eia import fetch_eia_brent_vintages
from oil_forecast_project.data_sources.fred import fetch_brent_spot_daily, fetch_cpi_monthly
from oil_forecast_project.data_sources.market import fetch_brent_front_month_futures
from oil_forecast_project.data_sources.world_bank import fetch_world_bank_oil_average_forecasts
from oil_forecast_project.io import write_csv


TARGET_REAL_YEAR = 2025


def build_annual_cpi(cpi_monthly: pd.DataFrame) -> pd.DataFrame:
    annual = (
        cpi_monthly.assign(year=cpi_monthly["date"].dt.year)
        .groupby("year", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "cpi_avg"})
    )
    target_cpi = annual.loc[annual["year"] == TARGET_REAL_YEAR, "cpi_avg"].iloc[0]
    annual["to_2025_factor"] = target_cpi / annual["cpi_avg"]
    return annual


def build_monthly_cpi(cpi_monthly: pd.DataFrame) -> pd.DataFrame:
    target_cpi = cpi_monthly.loc[cpi_monthly["date"].dt.year == TARGET_REAL_YEAR, "value"].mean()
    monthly = cpi_monthly.copy()
    monthly["year"] = monthly["date"].dt.year
    monthly["month"] = monthly["date"].dt.month
    monthly["to_2025_factor"] = target_cpi / monthly["value"]
    return monthly[["date", "year", "month", "value", "to_2025_factor"]]


def build_actual_brent_annual(brent_daily: pd.DataFrame, annual_cpi: pd.DataFrame) -> pd.DataFrame:
    actual = (
        brent_daily.dropna(subset=["value"])
        .assign(year=brent_daily["date"].dt.year)
        .groupby("year", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "actual_nominal_usd_per_bbl"})
        .merge(annual_cpi[["year", "to_2025_factor"]], on="year", how="left")
    )
    actual["actual_real_2025_usd_per_bbl"] = actual["actual_nominal_usd_per_bbl"] * actual["to_2025_factor"]
    return actual


def build_release_month_features(
    brent_daily: pd.DataFrame,
    futures_daily: pd.DataFrame,
    monthly_cpi: pd.DataFrame,
    eia_vintages: pd.DataFrame,
) -> pd.DataFrame:
    known_releases = eia_vintages[["vintage_year", "release_date"]].drop_duplicates().copy()
    min_year = int(min(brent_daily["date"].dt.year.min(), futures_daily["date"].dt.year.min()))
    max_year = int(max(brent_daily["date"].dt.year.max(), futures_daily["date"].dt.year.max()))
    release_rows = []
    known_release_map = dict(zip(known_releases["vintage_year"], known_releases["release_date"]))
    for year in range(min_year, max_year + 1):
        if year in known_release_map:
            release_date = pd.Timestamp(known_release_map[year])
        else:
            release_date = pd.Timestamp(f"{year}-01-15")
        release_rows.append({"vintage_year": year, "release_date": release_date})
    release_months = pd.DataFrame(release_rows)
    release_months["year"] = release_months["release_date"].dt.year
    release_months["month"] = release_months["release_date"].dt.month

    spot_monthly = (
        brent_daily.dropna(subset=["value"])
        .assign(year=brent_daily["date"].dt.year, month=brent_daily["date"].dt.month)
        .groupby(["year", "month"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "spot_release_month_nominal"})
    )
    futures_monthly = (
        futures_daily.dropna(subset=["close"])
        .assign(year=futures_daily["date"].dt.year, month=futures_daily["date"].dt.month)
        .groupby(["year", "month"], as_index=False)["close"]
        .mean()
        .rename(columns={"close": "futures_release_month_nominal"})
    )

    features = (
        release_months.merge(spot_monthly, on=["year", "month"], how="left")
        .merge(futures_monthly, on=["year", "month"], how="left")
        .merge(monthly_cpi[["year", "month", "to_2025_factor"]], on=["year", "month"], how="left")
    )
    features["spot_release_month_real_2025"] = features["spot_release_month_nominal"] * features["to_2025_factor"]
    features["futures_release_month_real_2025"] = features["futures_release_month_nominal"] * features["to_2025_factor"]
    return features[
        [
            "vintage_year",
            "release_date",
            "spot_release_month_nominal",
            "futures_release_month_nominal",
            "spot_release_month_real_2025",
            "futures_release_month_real_2025",
        ]
    ]


def build_eia_forecast_dataset() -> dict[str, pd.DataFrame]:
    eia = fetch_eia_brent_vintages(start_year=2013, end_year=2026)
    brent_daily = fetch_brent_spot_daily()
    cpi_monthly = fetch_cpi_monthly()
    futures_daily = fetch_brent_front_month_futures()
    world_bank = fetch_world_bank_oil_average_forecasts()

    annual_cpi = build_annual_cpi(cpi_monthly)
    monthly_cpi = build_monthly_cpi(cpi_monthly)
    actual = build_actual_brent_annual(brent_daily, annual_cpi)
    release_features = build_release_month_features(brent_daily, futures_daily, monthly_cpi, eia)

    eia = eia.merge(
        annual_cpi.rename(columns={"year": "table12_base_year"})[["table12_base_year", "to_2025_factor"]],
        on="table12_base_year",
        how="left",
    )
    eia["forecast_real_2025_usd_per_bbl"] = eia["forecast_real_base"] * eia["to_2025_factor"]
    eia["horizon_years"] = eia["target_year"] - eia["vintage_year"]
    eia["benchmark_anchor_year"] = eia["vintage_year"] - 1
    eia = eia.merge(actual[["year", "actual_real_2025_usd_per_bbl"]].rename(columns={"year": "target_year"}), on="target_year", how="left")
    eia = eia.merge(
        actual[["year", "actual_real_2025_usd_per_bbl"]].rename(
            columns={"year": "benchmark_anchor_year", "actual_real_2025_usd_per_bbl": "random_walk_forecast_real_2025"}
        ),
        on="benchmark_anchor_year",
        how="left",
    )
    eia = eia.merge(release_features, on=["vintage_year", "release_date"], how="left")
    eia["forecast_error"] = eia["forecast_real_2025_usd_per_bbl"] - eia["actual_real_2025_usd_per_bbl"]
    eia["random_walk_error"] = eia["random_walk_forecast_real_2025"] - eia["actual_real_2025_usd_per_bbl"]

    for df_name, df in {
        "eia_brent_forecasts.csv": eia,
        "actual_brent_annual.csv": actual,
        "annual_cpi.csv": annual_cpi,
        "release_month_features.csv": release_features,
        "world_bank_oil_average_forecasts.csv": world_bank,
    }.items():
        write_csv(df, PROCESSED_DIR / df_name)

    return {
        "eia": eia,
        "actual": actual,
        "annual_cpi": annual_cpi,
        "monthly_cpi": monthly_cpi,
        "release_features": release_features,
        "world_bank": world_bank,
        "futures_daily": futures_daily,
        "brent_daily": brent_daily,
    }


def build_evaluation_panel(eia: pd.DataFrame) -> pd.DataFrame:
    panel = eia.loc[eia["horizon_years"].isin([3, 5])].dropna(
        subset=["actual_real_2025_usd_per_bbl", "forecast_real_2025_usd_per_bbl", "random_walk_forecast_real_2025"]
    ).copy()
    panel["absolute_error"] = panel["forecast_error"].abs()
    panel["squared_error"] = panel["forecast_error"] ** 2
    panel["benchmark_absolute_error"] = panel["random_walk_error"].abs()
    panel["benchmark_squared_error"] = panel["random_walk_error"] ** 2
    return panel.sort_values(["horizon_years", "vintage_year"]).reset_index(drop=True)


def write_benchmark_summary(panel: pd.DataFrame) -> pd.DataFrame:
    eia_summary = summarize_errors(
        panel,
        provider_label="EIA",
        forecast_col="forecast_real_2025_usd_per_bbl",
        error_col="forecast_error",
    )
    random_walk_frame = panel[
        ["horizon_years", "actual_real_2025_usd_per_bbl", "random_walk_forecast_real_2025", "random_walk_error"]
    ].rename(
        columns={
            "random_walk_forecast_real_2025": "forecast_real_2025_usd_per_bbl",
            "random_walk_error": "forecast_error",
        }
    )
    rw_summary = summarize_errors(
        random_walk_frame,
        provider_label="Martingale",
        forecast_col="forecast_real_2025_usd_per_bbl",
        error_col="forecast_error",
    )
    summary = pd.concat([eia_summary, rw_summary], ignore_index=True)
    write_csv(summary, PROCESSED_DIR / "benchmark_metrics.csv")
    return summary
