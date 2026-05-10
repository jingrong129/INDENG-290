# Source Code

The local project folder contains the reproducible Python package under `src/oil_forecast_project/`.

Main modules:

- `data_sources/eia.py`: downloads and parses EIA AEO Table 12 Brent forecast vintages.
- `data_sources/fred.py`: loads Brent spot and CPI series from FRED.
- `data_sources/market.py`: prepares Brent front-month futures features.
- `data_sources/world_bank.py`: downloads supplementary World Bank oil forecast data.
- `datasets.py`: standardizes forecasts, realizations, and evaluation panels.
- `analysis/metrics.py`: computes ME, MPE, MAE, RMSE, and MAPE.
- `analysis/models.py`: runs rolling AR and futures-augmented forecast models.
- `analysis/additional.py`: runs recursive bias correction and CPI diagnostics.
- `pipeline.py`: orchestrates the full analysis pipeline.
