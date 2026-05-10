import pandas as pd
import pytest

from oil_forecast_project.analysis.metrics import summarize_errors


def test_summarize_errors_returns_expected_columns():
    frame = pd.DataFrame(
        {
            "horizon_years": [3, 3, 5, 5],
            "actual_real_2025_usd_per_bbl": [10.0, 20.0, 30.0, 40.0],
            "forecast_real_2025_usd_per_bbl": [12.0, 18.0, 35.0, 39.0],
            "forecast_error": [2.0, -2.0, 5.0, -1.0],
        }
    )
    out = summarize_errors(
        frame,
        provider_label="TestModel",
        forecast_col="forecast_real_2025_usd_per_bbl",
        error_col="forecast_error",
    )

    assert list(out.columns) == ["model", "horizon_years", "n_forecasts", "ME", "MPE", "MAE", "RMSE", "MAPE"]
    assert set(out["horizon_years"]) == {3, 5}

    horizon_3 = out.loc[out["horizon_years"] == 3].iloc[0]
    assert horizon_3["model"] == "TestModel"
    assert horizon_3["n_forecasts"] == 2
    assert horizon_3["ME"] == pytest.approx(0.0)
    assert horizon_3["MPE"] == pytest.approx(0.05)
    assert horizon_3["MAE"] == pytest.approx(2.0)
    assert horizon_3["RMSE"] == pytest.approx(2.0)
    assert horizon_3["MAPE"] == pytest.approx(0.15)
