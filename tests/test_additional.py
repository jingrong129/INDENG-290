import pandas as pd
import pytest

from oil_forecast_project.analysis.additional import build_bias_corrected_eia_forecasts, summarize_cpi_brent_relationship


def test_build_bias_corrected_eia_forecasts_uses_only_prior_errors():
    panel = pd.DataFrame(
        {
            "vintage_year": [2018, 2019, 2020, 2018, 2019, 2020],
            "release_date": pd.to_datetime(
                ["2018-01-01", "2019-01-01", "2020-01-01", "2018-01-01", "2019-01-01", "2020-01-01"]
            ),
            "horizon_years": [3, 3, 3, 5, 5, 5],
            "forecast_real_2025_usd_per_bbl": [100.0, 110.0, 120.0, 90.0, 95.0, 105.0],
            "actual_real_2025_usd_per_bbl": [90.0, 100.0, 115.0, 80.0, 90.0, 100.0],
            "forecast_error": [10.0, 10.0, 5.0, 10.0, 5.0, 5.0],
        }
    )

    corrected, metrics = build_bias_corrected_eia_forecasts(panel)

    horizon_3_2020 = corrected.loc[(corrected["horizon_years"] == 3) & (corrected["vintage_year"] == 2020)].iloc[0]
    assert horizon_3_2020["historical_mean_error"] == pytest.approx(10.0)
    assert horizon_3_2020["bias_corrected_forecast_real_2025_usd_per_bbl"] == pytest.approx(110.0)
    assert horizon_3_2020["bias_corrected_error"] == pytest.approx(-5.0)
    assert set(metrics["horizon_years"]) == {3, 5}


def test_summarize_cpi_brent_relationship_returns_expected_metrics():
    actual = pd.DataFrame(
        {
            "year": [2023, 2024, 2025],
            "actual_nominal_usd_per_bbl": [80.0, 100.0, 110.0],
            "actual_real_2025_usd_per_bbl": [90.0, 105.0, 110.0],
        }
    )
    annual_cpi = pd.DataFrame({"year": [2023, 2024, 2025], "cpi_avg": [280.0, 300.0, 330.0]})

    relationship, summary = summarize_cpi_brent_relationship(actual, annual_cpi)

    assert "cpi_inflation_yoy" in relationship.columns
    assert "nominal_brent_growth_yoy" in relationship.columns
    assert set(summary["metric"]) == {
        "corr_nominal_brent_level_vs_cpi_level",
        "corr_nominal_brent_growth_vs_cpi_inflation",
        "corr_real_brent_growth_vs_cpi_inflation",
        "avg_deflation_gap_usd_per_bbl",
        "median_deflation_gap_usd_per_bbl",
    }
