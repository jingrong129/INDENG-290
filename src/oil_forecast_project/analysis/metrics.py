from __future__ import annotations

import math

import pandas as pd


def _rmse(series: pd.Series) -> float:
    return math.sqrt((series**2).mean())


def summarize_errors(
    frame: pd.DataFrame,
    provider_label: str,
    forecast_col: str,
    error_col: str,
) -> pd.DataFrame:
    records: list[dict[str, float | int | str]] = []
    for horizon, group in frame.groupby("horizon_years"):
        error = group[error_col]
        actual = group["actual_real_2025_usd_per_bbl"]
        forecast = group[forecast_col]
        percentage_error = error / actual
        mape = ((forecast - actual).abs() / actual).mean()
        records.append(
            {
                "model": provider_label,
                "horizon_years": int(horizon),
                "n_forecasts": int(len(group)),
                "ME": error.mean(),
                "MPE": percentage_error.mean(),
                "MAE": error.abs().mean(),
                "RMSE": _rmse(error),
                "MAPE": mape,
            }
        )
    return pd.DataFrame.from_records(records)
