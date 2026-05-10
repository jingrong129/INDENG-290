from __future__ import annotations

from pathlib import Path

import pandas as pd

from oil_forecast_project.analysis.additional import build_bias_corrected_eia_forecasts, summarize_cpi_brent_relationship
from oil_forecast_project.analysis.models import fit_rolling_models
from oil_forecast_project.analysis.plots import (
    plot_benchmark_metrics,
    plot_bias_correction_metrics,
    plot_cpi_brent_relationship,
    plot_eia_vintages,
    plot_model_comparison,
)
from oil_forecast_project.config import OUTPUTS_DIR, PROCESSED_DIR
from oil_forecast_project.datasets import build_eia_forecast_dataset, build_evaluation_panel, write_benchmark_summary
from oil_forecast_project.io import write_csv, write_excel


def _write_project_summary(
    benchmark_metrics: pd.DataFrame,
    bias_corrected_metrics: pd.DataFrame,
    rolling_metrics: pd.DataFrame,
    cpi_brent_summary: pd.DataFrame,
    panel: pd.DataFrame,
) -> Path:
    summary_lines = [
        "# Oil Forecast Evaluation Summary",
        "",
        "## Main dataset",
        f"- EIA Brent vintages: {panel['vintage_year'].nunique()} publication years used in realized evaluation",
        f"- Forecast observations used in 3y/5y evaluation: {len(panel)}",
        "",
        "## Benchmark results",
        benchmark_metrics.to_string(index=False),
        "",
        "## Bias-corrected EIA results",
        bias_corrected_metrics.to_string(index=False) if not bias_corrected_metrics.empty else "No bias-corrected metrics were generated.",
        "",
        "## Rolling model results",
        rolling_metrics.to_string(index=False) if not rolling_metrics.empty else "No rolling model metrics were generated.",
        "",
        "## CPI and Brent relationship checks",
        cpi_brent_summary.to_string(index=False),
        "",
        "## Notes",
        "- Main analysis uses EIA Brent Spot forecasts from AEO Table 12, deflated to 2025 dollars with CPI.",
        "- Realized annual Brent prices come from FRED DCOILBRENTEU aggregated to annual averages.",
        "- The naive benchmark is treated as a martingale or no-change benchmark: the forecast equals the latest completed annual Brent price available at release.",
        "- Bias-corrected EIA forecasts are estimated with an expanding-window historical mean error by horizon, using only prior forecast errors to avoid look-ahead bias.",
        "- The market-augmented model uses Brent front-month futures from Yahoo Finance (`BZ=F`) as a market-information proxy.",
        "- World Bank archive data are downloaded as supplementary material because the forecast object is `Crude oil, avg`, not exact Brent.",
        "- Relative project ranking cannot be tested empirically in this repo because no project-level cash-flow panel is included; the current code only supports forecast-side evaluation.",
    ]
    path = OUTPUTS_DIR / "project_summary.md"
    path.write_text("\n".join(summary_lines))
    return path


def run_pipeline() -> None:
    bundle = build_eia_forecast_dataset()
    panel = build_evaluation_panel(bundle["eia"])
    benchmark_metrics = write_benchmark_summary(panel)
    bias_corrected_panel, bias_corrected_metrics = build_bias_corrected_eia_forecasts(panel)
    rolling_predictions, rolling_metrics = fit_rolling_models(bundle["actual"], bundle["release_features"])
    cpi_brent_relationship, cpi_brent_summary = summarize_cpi_brent_relationship(bundle["actual"], bundle["annual_cpi"])
    write_csv(bias_corrected_panel, PROCESSED_DIR / "bias_corrected_eia_predictions.csv")
    write_csv(bias_corrected_metrics, PROCESSED_DIR / "bias_corrected_metrics.csv")
    write_csv(cpi_brent_relationship, PROCESSED_DIR / "cpi_brent_relationship.csv")
    write_csv(cpi_brent_summary, PROCESSED_DIR / "cpi_brent_summary.csv")

    plot_eia_vintages(panel, bundle["actual"])
    plot_benchmark_metrics(benchmark_metrics)
    plot_bias_correction_metrics(pd.concat([benchmark_metrics, bias_corrected_metrics], ignore_index=True))
    plot_cpi_brent_relationship(cpi_brent_relationship)
    if not rolling_metrics.empty:
        plot_model_comparison(rolling_metrics)
    _write_project_summary(benchmark_metrics, bias_corrected_metrics, rolling_metrics, cpi_brent_summary, panel)

    write_excel(
        OUTPUTS_DIR / "analysis_outputs.xlsx",
        {
            "eia_eval_panel": panel,
            "benchmark_metrics": benchmark_metrics,
            "bias_corrected_panel": bias_corrected_panel,
            "bias_corrected_metrics": bias_corrected_metrics,
            "rolling_predictions": rolling_predictions,
            "rolling_metrics": rolling_metrics,
            "actual_brent": bundle["actual"],
            "cpi_brent_relationship": cpi_brent_relationship,
            "cpi_brent_summary": cpi_brent_summary,
            "eia_full": bundle["eia"],
            "world_bank": bundle["world_bank"],
        },
    )
