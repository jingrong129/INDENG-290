# Improving Long-Term Oil Price Forecasts

Final Project Report appendix repository links updated for `jingrong129/INDENG-290`.

## Executive Summary

This project evaluates whether long-horizon oil price forecasts are decision-useful for upstream oil and gas investment planning. The analysis focuses on EIA Annual Energy Outlook Brent forecast vintages because they provide the cleanest publicly accessible long-horizon archive. Forecasts and realized annual Brent prices are converted into real 2025 dollars using CPI, then evaluated at 3-year and 5-year horizons against a martingale benchmark.

Main findings:

- EIA beats the martingale benchmark on RMSE at both 3-year and 5-year horizons.
- EIA forecasts are systematically optimistic in the realized sample.
- A recursive historical bias correction improves forecast accuracy, especially at the 5-year horizon.
- Rolling AR and rolling AR plus futures models do not outperform EIA in the current implementation.

## Live Links To The Data Repository

- Project data repository root: <https://github.com/jingrong129/INDENG-290/tree/main/data>
- Processed data directory: <https://github.com/jingrong129/INDENG-290/tree/main/data/processed>
- Raw EIA archive documentation: <https://github.com/jingrong129/INDENG-290/tree/main/data/raw/eia>

## Appendix Repository Links

- GitHub repository: <https://github.com/jingrong129/INDENG-290>
- Source code directory: <https://github.com/jingrong129/INDENG-290/tree/main/src>
- Data directory: <https://github.com/jingrong129/INDENG-290/tree/main/data>
- Processed data directory: <https://github.com/jingrong129/INDENG-290/tree/main/data/processed>
- Summary output: <https://github.com/jingrong129/INDENG-290/blob/main/outputs/project_summary.md>
- Benchmark metrics CSV: <https://github.com/jingrong129/INDENG-290/blob/main/data/processed/benchmark_metrics.csv>
- Bias-corrected metrics CSV: <https://github.com/jingrong129/INDENG-290/blob/main/data/processed/bias_corrected_metrics.csv>
- Rolling-model metrics CSV: <https://github.com/jingrong129/INDENG-290/blob/main/data/processed/rolling_model_metrics.csv>

## Key Metrics

| Model | Horizon | N | ME | MPE | MAE | RMSE | MAPE |
|---|---:|---:|---:|---:|---:|---:|---:|
| EIA | 3y | 11 | 20.44 | 0.330 | 26.01 | 34.97 | 0.388 |
| Martingale | 3y | 11 | 17.25 | 0.276 | 31.66 | 42.99 | 0.438 |
| EIA | 5y | 9 | 26.64 | 0.365 | 28.09 | 34.32 | 0.381 |
| Martingale | 5y | 9 | 13.79 | 0.248 | 38.90 | 47.34 | 0.512 |
| Bias-Corrected EIA | 3y | 10 | -27.93 | -0.315 | 29.26 | 33.65 | 0.341 |
| Bias-Corrected EIA | 5y | 8 | -19.33 | -0.212 | 20.53 | 25.36 | 0.235 |

## Data Sources

- EIA AEO Table 12 archive and current release: <https://www.eia.gov/outlooks/aeo/tables_ref.php> and <https://www.eia.gov/outlooks/archive/>
- FRED Brent spot series `DCOILBRENTEU`
- FRED CPI series `CPIAUCSL`
- Yahoo Finance Brent front-month futures ticker `BZ=F`
- World Bank commodity price forecast archive: <https://www.worldbank.org/en/research/commodity-markets/price-forecasts>
