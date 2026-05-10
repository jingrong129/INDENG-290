from __future__ import annotations

import pandas as pd

from oil_forecast_project.analysis.metrics import summarize_errors


def build_bias_corrected_eia_forecasts(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    corrected = panel.sort_values(["horizon_years", "release_date", "vintage_year"]).copy()
    grouped_errors = corrected.groupby("horizon_years")["forecast_error"]
    corrected["historical_mean_error"] = grouped_errors.transform(lambda series: series.shift(1).expanding().mean())
    corrected["historical_error_count"] = grouped_errors.transform(lambda series: series.shift(1).expanding().count())
    corrected["bias_corrected_forecast_real_2025_usd_per_bbl"] = (
        corrected["forecast_real_2025_usd_per_bbl"] - corrected["historical_mean_error"]
    )
    corrected["bias_corrected_error"] = (
        corrected["bias_corrected_forecast_real_2025_usd_per_bbl"] - corrected["actual_real_2025_usd_per_bbl"]
    )

    evaluated = corrected.dropna(subset=["bias_corrected_forecast_real_2025_usd_per_bbl"]).copy()
    metrics = summarize_errors(
        evaluated,
        provider_label="Bias-Corrected EIA",
        forecast_col="bias_corrected_forecast_real_2025_usd_per_bbl",
        error_col="bias_corrected_error",
    )
    return corrected, metrics


def summarize_cpi_brent_relationship(actual: pd.DataFrame, annual_cpi: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    joined = actual.merge(annual_cpi[["year", "cpi_avg"]], on="year", how="inner").sort_values("year").copy()
    joined["cpi_inflation_yoy"] = joined["cpi_avg"].pct_change()
    joined["nominal_brent_growth_yoy"] = joined["actual_nominal_usd_per_bbl"].pct_change()
    joined["real_brent_growth_yoy"] = joined["actual_real_2025_usd_per_bbl"].pct_change()
    joined["deflation_gap_usd_per_bbl"] = joined["actual_real_2025_usd_per_bbl"] - joined["actual_nominal_usd_per_bbl"]

    growth = joined.dropna(
        subset=["cpi_inflation_yoy", "nominal_brent_growth_yoy", "real_brent_growth_yoy"]
    ).copy()
    summary = pd.DataFrame(
        [
            {
                "metric": "corr_nominal_brent_level_vs_cpi_level",
                "value": joined["actual_nominal_usd_per_bbl"].corr(joined["cpi_avg"]),
                "interpretation": "Level correlation is descriptive only and may reflect common time trends.",
            },
            {
                "metric": "corr_nominal_brent_growth_vs_cpi_inflation",
                "value": growth["nominal_brent_growth_yoy"].corr(growth["cpi_inflation_yoy"]),
                "interpretation": "Year-over-year co-movement between nominal Brent growth and CPI inflation.",
            },
            {
                "metric": "corr_real_brent_growth_vs_cpi_inflation",
                "value": growth["real_brent_growth_yoy"].corr(growth["cpi_inflation_yoy"]),
                "interpretation": "Checks whether CPI comovement remains after converting Brent into real terms.",
            },
            {
                "metric": "avg_deflation_gap_usd_per_bbl",
                "value": joined["deflation_gap_usd_per_bbl"].mean(),
                "interpretation": "Average difference between real-2025 and nominal annual Brent prices.",
            },
            {
                "metric": "median_deflation_gap_usd_per_bbl",
                "value": joined["deflation_gap_usd_per_bbl"].median(),
                "interpretation": "Median real-versus-nominal adjustment across annual observations.",
            },
        ]
    )
    return joined, summary
