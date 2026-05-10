from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from oil_forecast_project.analysis.metrics import summarize_errors
from oil_forecast_project.config import PROCESSED_DIR
from oil_forecast_project.io import write_csv


def _build_origin_feature_table(actual: pd.DataFrame, release_features: pd.DataFrame) -> pd.DataFrame:
    prices = actual[["year", "actual_real_2025_usd_per_bbl"]].rename(columns={"year": "price_year"})
    release = release_features.copy()
    release["origin_year"] = release["vintage_year"]
    release["last_complete_year"] = release["origin_year"] - 1

    feature_rows: list[dict[str, float | int | pd.Timestamp]] = []
    price_map = dict(zip(prices["price_year"], prices["actual_real_2025_usd_per_bbl"]))
    release_map = release.set_index("origin_year").to_dict("index")
    min_year = int(prices["price_year"].min())
    max_year = int(prices["price_year"].max())
    for origin_year in range(min_year + 6, max_year + 1):
        if origin_year not in release_map:
            continue
        last_complete = origin_year - 1
        needed_years = [last_complete - i for i in range(5)]
        if not all(year in price_map for year in needed_years):
            continue
        release_row = release_map[origin_year]
        lag1 = price_map[last_complete]
        lag2 = price_map[last_complete - 1]
        lag3 = price_map[last_complete - 2]
        lag5_mean = np.mean([price_map[last_complete - i] for i in range(5)])
        mom_1y = lag1 / lag2 - 1
        futures_real = release_row.get("futures_release_month_real_2025")
        basis = futures_real - lag1 if pd.notna(futures_real) else np.nan
        feature_rows.append(
            {
                "origin_year": origin_year,
                "release_date": release_row["release_date"],
                "lag1": lag1,
                "lag2": lag2,
                "lag3": lag3,
                "lag5_mean": lag5_mean,
                "mom_1y": mom_1y,
                "futures_release_month_real_2025": futures_real,
                "basis_real_2025": basis,
            }
        )
    return pd.DataFrame(feature_rows)


def _rolling_predictions(
    origin_features: pd.DataFrame,
    actual: pd.DataFrame,
    horizon: int,
    feature_cols: list[str],
    model_name: str,
) -> pd.DataFrame:
    target_map = dict(zip(actual["year"], actual["actual_real_2025_usd_per_bbl"]))
    rows: list[dict[str, float | int | str | pd.Timestamp]] = []
    model_frame = origin_features.copy()
    model_frame["target_year"] = model_frame["origin_year"] + horizon
    model_frame["actual_real_2025_usd_per_bbl"] = model_frame["target_year"].map(target_map)
    model_frame = model_frame.dropna(subset=["actual_real_2025_usd_per_bbl"] + feature_cols).sort_values("origin_year")

    for _, row in model_frame.iterrows():
        train = model_frame[model_frame["origin_year"] < row["origin_year"]].dropna(subset=feature_cols)
        if len(train) < 5:
            continue
        reg = LinearRegression()
        reg.fit(train[feature_cols], train["actual_real_2025_usd_per_bbl"])
        forecast = float(reg.predict(pd.DataFrame([row[feature_cols]], columns=feature_cols))[0])
        error = forecast - row["actual_real_2025_usd_per_bbl"]
        rows.append(
            {
                "model": model_name,
                "origin_year": int(row["origin_year"]),
                "release_date": row["release_date"],
                "horizon_years": horizon,
                "target_year": int(row["target_year"]),
                "forecast_real_2025_usd_per_bbl": forecast,
                "actual_real_2025_usd_per_bbl": float(row["actual_real_2025_usd_per_bbl"]),
                "forecast_error": error,
            }
        )
    return pd.DataFrame(rows)


def fit_rolling_models(actual: pd.DataFrame, release_features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    origin_features = _build_origin_feature_table(actual, release_features)
    prediction_frames = []
    specs = [
        ("Rolling AR", ["lag1", "lag2", "lag3"]),
        ("Rolling AR + Futures", ["lag1", "lag2", "lag3", "futures_release_month_real_2025", "basis_real_2025"]),
    ]
    for horizon in [3, 5]:
        for model_name, feature_cols in specs:
            prediction_frames.append(_rolling_predictions(origin_features, actual, horizon, feature_cols, model_name))

    predictions = pd.concat([frame for frame in prediction_frames if not frame.empty], ignore_index=True)
    metrics = []
    for model_name, group in predictions.groupby("model"):
        metrics.append(
            summarize_errors(
                group.assign(horizon_years=group["horizon_years"]),
                provider_label=model_name,
                forecast_col="forecast_real_2025_usd_per_bbl",
                error_col="forecast_error",
            )
        )
    metrics_df = pd.concat(metrics, ignore_index=True) if metrics else pd.DataFrame()
    write_csv(predictions, PROCESSED_DIR / "rolling_model_predictions.csv")
    write_csv(metrics_df, PROCESSED_DIR / "rolling_model_metrics.csv")
    return predictions, metrics_df
