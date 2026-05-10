from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from oil_forecast_project.config import OUTPUTS_DIR


sns.set_theme(style="whitegrid")


def plot_eia_vintages(panel: pd.DataFrame, actual: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(12, 7))
    for vintage_year, group in panel.groupby("vintage_year"):
        ax.plot(group["target_year"], group["forecast_real_2025_usd_per_bbl"], alpha=0.25, color="#1f78b4")
    ax.plot(actual["year"], actual["actual_real_2025_usd_per_bbl"], color="#111111", linewidth=2.5, label="Actual Brent")
    ax.set_title("EIA Brent forecast vintages vs realized Brent")
    ax.set_xlabel("Target year")
    ax.set_ylabel("Real 2025 USD per barrel")
    ax.legend()
    path = OUTPUTS_DIR / "eia_vintages_vs_actual.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_benchmark_metrics(metrics: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)
    subset = metrics.copy()
    sns.barplot(data=subset, x="model", y="RMSE", hue="horizon_years", ax=axes[0], palette="crest")
    sns.barplot(data=subset, x="model", y="ME", hue="horizon_years", ax=axes[1], palette="flare")
    axes[0].set_title("RMSE by horizon")
    axes[1].set_title("Mean error by horizon")
    axes[0].set_xlabel("")
    axes[1].set_xlabel("")
    axes[0].set_ylabel("Real 2025 USD per barrel")
    axes[1].set_ylabel("Real 2025 USD per barrel")
    for ax in axes:
        ax.tick_params(axis="x", rotation=15)
    path = OUTPUTS_DIR / "benchmark_metrics.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_model_comparison(metrics: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=metrics, x="model", y="RMSE", hue="horizon_years", ax=ax, palette="mako")
    ax.set_title("Rolling model RMSE by horizon")
    ax.set_xlabel("")
    ax.set_ylabel("Real 2025 USD per barrel")
    ax.tick_params(axis="x", rotation=15)
    path = OUTPUTS_DIR / "rolling_model_rmse.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_bias_correction_metrics(metrics: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
    sns.barplot(data=metrics, x="model", y="RMSE", hue="horizon_years", ax=axes[0], palette="viridis")
    sns.barplot(data=metrics, x="model", y="MPE", hue="horizon_years", ax=axes[1], palette="rocket")
    axes[0].set_title("RMSE comparison including bias correction")
    axes[1].set_title("Mean percentage error comparison")
    axes[0].set_xlabel("")
    axes[1].set_xlabel("")
    axes[0].set_ylabel("Real 2025 USD per barrel")
    axes[1].set_ylabel("Share of actual price")
    for ax in axes:
        ax.tick_params(axis="x", rotation=15)
    path = OUTPUTS_DIR / "bias_correction_metrics.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_cpi_brent_relationship(relationship: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    left = relationship.dropna(subset=["cpi_inflation_yoy", "nominal_brent_growth_yoy"])
    right = relationship.dropna(subset=["year", "actual_nominal_usd_per_bbl", "actual_real_2025_usd_per_bbl"])

    sns.regplot(
        data=left,
        x="nominal_brent_growth_yoy",
        y="cpi_inflation_yoy",
        ax=axes[0],
        scatter_kws={"s": 55, "alpha": 0.8},
        line_kws={"color": "#c44e52"},
    )
    axes[0].set_title("Brent growth vs CPI inflation")
    axes[0].set_xlabel("Nominal Brent YoY growth")
    axes[0].set_ylabel("CPI YoY inflation")

    axes[1].plot(right["year"], right["actual_nominal_usd_per_bbl"], label="Nominal Brent", color="#4c72b0", linewidth=2)
    axes[1].plot(
        right["year"],
        right["actual_real_2025_usd_per_bbl"],
        label="Real Brent (2025 USD)",
        color="#dd8452",
        linewidth=2,
    )
    axes[1].set_title("Nominal vs real annual Brent")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("USD per barrel")
    axes[1].legend()

    path = OUTPUTS_DIR / "cpi_brent_relationship.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path
