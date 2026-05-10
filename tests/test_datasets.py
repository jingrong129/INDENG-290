import pandas as pd
import pytest

from oil_forecast_project import datasets


def test_build_annual_cpi_converts_to_2025_dollars():
    cpi_monthly = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2025-01-01", "2025-02-01"]),
            "value": [100.0, 100.0, 200.0, 200.0],
        }
    )

    annual = datasets.build_annual_cpi(cpi_monthly)

    factors = dict(zip(annual["year"], annual["to_2025_factor"]))
    assert factors[2024] == pytest.approx(2.0)
    assert factors[2025] == pytest.approx(1.0)


def test_build_actual_brent_annual_aggregates_and_deflates():
    brent_daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2025-01-01"]),
            "value": [70.0, 90.0, None, 100.0],
        }
    )
    annual_cpi = pd.DataFrame({"year": [2024, 2025], "to_2025_factor": [1.5, 1.0]})

    actual = datasets.build_actual_brent_annual(brent_daily, annual_cpi)

    row_2024 = actual.loc[actual["year"] == 2024].iloc[0]
    assert row_2024["actual_nominal_usd_per_bbl"] == pytest.approx(80.0)
    assert row_2024["actual_real_2025_usd_per_bbl"] == pytest.approx(120.0)


def test_build_release_month_features_uses_known_release_month_and_real_prices():
    brent_daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-04-01", "2024-04-15", "2025-01-15"]),
            "value": [80.0, 100.0, 120.0],
        }
    )
    futures_daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-04-03", "2024-04-17", "2025-01-15"]),
            "close": [90.0, 110.0, 130.0],
        }
    )
    monthly_cpi = pd.DataFrame(
        {
            "year": [2024, 2025],
            "month": [4, 1],
            "to_2025_factor": [1.25, 1.0],
        }
    )
    eia_vintages = pd.DataFrame({"vintage_year": [2024], "release_date": pd.to_datetime(["2024-04-20"])})

    features = datasets.build_release_month_features(brent_daily, futures_daily, monthly_cpi, eia_vintages)

    row_2024 = features.loc[features["vintage_year"] == 2024].iloc[0]
    assert row_2024["spot_release_month_nominal"] == pytest.approx(90.0)
    assert row_2024["futures_release_month_nominal"] == pytest.approx(100.0)
    assert row_2024["spot_release_month_real_2025"] == pytest.approx(112.5)
    assert row_2024["futures_release_month_real_2025"] == pytest.approx(125.0)


def test_build_evaluation_panel_filters_horizons_and_requires_realized_values():
    eia = pd.DataFrame(
        {
            "vintage_year": [2020, 2021, 2022, 2023],
            "target_year": [2023, 2026, 2026, 2025],
            "horizon_years": [3, 5, 4, 2],
            "forecast_real_2025_usd_per_bbl": [80.0, 90.0, 95.0, 70.0],
            "actual_real_2025_usd_per_bbl": [100.0, 120.0, 130.0, None],
            "random_walk_forecast_real_2025": [75.0, 85.0, 88.0, 60.0],
            "forecast_error": [-20.0, -30.0, -35.0, None],
            "random_walk_error": [-25.0, -35.0, -42.0, None],
        }
    )

    panel = datasets.build_evaluation_panel(eia)

    assert list(panel["horizon_years"]) == [3, 5]
    assert list(panel["vintage_year"]) == [2020, 2021]
    assert panel.loc[0, "absolute_error"] == pytest.approx(20.0)
    assert panel.loc[1, "squared_error"] == pytest.approx(900.0)
    assert panel.loc[0, "benchmark_absolute_error"] == pytest.approx(25.0)
    assert panel.loc[1, "benchmark_squared_error"] == pytest.approx(1225.0)


def test_write_benchmark_summary_compares_eia_and_random_walk(tmp_path, monkeypatch):
    monkeypatch.setattr(datasets, "PROCESSED_DIR", tmp_path)
    panel = pd.DataFrame(
        {
            "horizon_years": [3, 3],
            "actual_real_2025_usd_per_bbl": [100.0, 200.0],
            "forecast_real_2025_usd_per_bbl": [110.0, 180.0],
            "forecast_error": [10.0, -20.0],
            "random_walk_forecast_real_2025": [90.0, 190.0],
            "random_walk_error": [-10.0, -10.0],
        }
    )

    summary = datasets.write_benchmark_summary(panel)

    assert (tmp_path / "benchmark_metrics.csv").exists()
    assert set(summary["model"]) == {"EIA", "Martingale"}
    eia = summary.loc[summary["model"] == "EIA"].iloc[0]
    random_walk = summary.loc[summary["model"] == "Martingale"].iloc[0]
    assert eia["ME"] == pytest.approx(-5.0)
    assert eia["MAE"] == pytest.approx(15.0)
    assert random_walk["ME"] == pytest.approx(-10.0)
    assert random_walk["RMSE"] == pytest.approx(10.0)
