# Oil Forecast Evaluation Summary

## Main dataset
- EIA Brent vintages: 11 publication years used in realized evaluation
- Forecast observations used in 3y/5y evaluation: 20

## Benchmark results
     model  horizon_years  n_forecasts        ME      MPE       MAE      RMSE     MAPE
       EIA              3           11 20.438661 0.330205 26.006072 34.974008 0.388205
       EIA              5            9 26.641034 0.365143 28.086861 34.321603 0.380629
Martingale              3           11 17.250898 0.275539 31.656702 42.989204 0.438045
Martingale              5            9 13.794846 0.248102 38.901808 47.341602 0.512064

## Bias-corrected EIA results
             model  horizon_years  n_forecasts         ME       MPE       MAE      RMSE     MAPE
Bias-Corrected EIA              3           10 -27.928878 -0.315293 29.255237 33.650298 0.340709
Bias-Corrected EIA              5            8 -19.332197 -0.212398 20.533071 25.358567 0.235410

## Rolling model results
               model  horizon_years  n_forecasts        ME       MPE       MAE      RMSE     MAPE
          Rolling AR              3           26 10.131831  0.157488 35.328167 48.951906 0.447015
          Rolling AR              5           24 -5.407059 -0.019203 35.948212 51.237855 0.379464
Rolling AR + Futures              3            9 17.960273  0.325135 40.109557 52.510599 0.549114
Rolling AR + Futures              5            7  7.571707  0.244169 36.614364 53.230335 0.539137

## CPI and Brent relationship checks
                                    metric     value                                                                interpretation
     corr_nominal_brent_level_vs_cpi_level  0.752935     Level correlation is descriptive only and may reflect common time trends.
corr_nominal_brent_growth_vs_cpi_inflation  0.519379    Year-over-year co-movement between nominal Brent growth and CPI inflation.
   corr_real_brent_growth_vs_cpi_inflation  0.475777 Checks whether CPI comovement remains after converting Brent into real terms.
             avg_deflation_gap_usd_per_bbl 23.631896         Average difference between real-2025 and nominal annual Brent prices.
          median_deflation_gap_usd_per_bbl 21.266521             Median real-versus-nominal adjustment across annual observations.

## Notes
- Main analysis uses EIA Brent Spot forecasts from AEO Table 12, deflated to 2025 dollars with CPI.
- Realized annual Brent prices come from FRED DCOILBRENTEU aggregated to annual averages.
- The naive benchmark is treated as a martingale or no-change benchmark: the forecast equals the latest completed annual Brent price available at release.
- Bias-corrected EIA forecasts are estimated with an expanding-window historical mean error by horizon, using only prior forecast errors to avoid look-ahead bias.
- The market-augmented model uses Brent front-month futures from Yahoo Finance (`BZ=F`) as a market-information proxy.
- World Bank archive data are downloaded as supplementary material because the forecast object is `Crude oil, avg`, not exact Brent.
- Relative project ranking cannot be tested empirically in this repo because no project-level cash-flow panel is included; the current code only supports forecast-side evaluation.