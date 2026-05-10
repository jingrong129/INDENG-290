from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "report_pipeline_flowchart.png"


def add_box(ax, x, y, w, h, title, body, facecolor):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.2,
        edgecolor="#4F6272",
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.68, title, ha="center", va="center", fontsize=12, fontweight="bold", color="#193549")
    ax.text(x + w / 2, y + h * 0.34, body, ha="center", va="center", fontsize=10, color="#193549", wrap=True)


def add_arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#5B7083"),
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(13.5, 7.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    add_box(ax, 0.04, 0.67, 0.18, 0.18, "Raw Forecast Data", "EIA AEO Table 12 vintages\nWorld Bank archive\nBrent futures history", "#EAF2FB")
    add_box(ax, 0.28, 0.67, 0.18, 0.18, "Raw Market Data", "FRED Brent spot\nFRED CPI series\nRelease-date alignment", "#EDF8F0")
    add_box(ax, 0.52, 0.67, 0.18, 0.18, "Data Standardization", "Annual averaging\nDeflation to 2025 USD\nFeature construction", "#FFF5E8")
    add_box(ax, 0.76, 0.67, 0.18, 0.18, "Evaluation Panel", "3-year and 5-year horizons\nMatched forecasts and realizations\nForecast errors", "#F7EEF8")

    add_box(ax, 0.10, 0.34, 0.22, 0.18, "Benchmark Analysis", "EIA vs martingale benchmark\nME, MPE, MAE, RMSE, MAPE", "#EEF4FC")
    add_box(ax, 0.39, 0.34, 0.22, 0.18, "Model Extensions", "Rolling AR\nRolling AR + Futures\nExpanding-window estimation", "#EEF8F1")
    add_box(ax, 0.68, 0.34, 0.22, 0.18, "Diagnostics", "Bias-corrected EIA\nCPI-Brent checks\nInterpretation for planning use", "#FFF7EA")

    add_box(ax, 0.28, 0.07, 0.44, 0.17, "Final Outputs", "Processed CSV files, Excel workbook, figures, presentation exhibits, and stakeholder-facing report conclusions", "#FFF9D9")

    add_arrow(ax, 0.22, 0.76, 0.28, 0.76)
    add_arrow(ax, 0.46, 0.76, 0.52, 0.76)
    add_arrow(ax, 0.70, 0.76, 0.76, 0.76)

    add_arrow(ax, 0.85, 0.67, 0.21, 0.52)
    add_arrow(ax, 0.85, 0.67, 0.50, 0.52)
    add_arrow(ax, 0.85, 0.67, 0.79, 0.52)

    add_arrow(ax, 0.21, 0.34, 0.40, 0.24)
    add_arrow(ax, 0.50, 0.34, 0.50, 0.24)
    add_arrow(ax, 0.79, 0.34, 0.60, 0.24)

    ax.text(0.5, 0.93, "Pipeline Overview: Improving Long-Term Oil Price Forecasts", ha="center", va="center", fontsize=16, fontweight="bold", color="#193549")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
