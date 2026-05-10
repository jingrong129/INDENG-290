# Improving Long-Term Oil Price Forecasts

Final Project Report

Repository: https://github.com/jingrong129/INDENG-290

## Executive Summary

This project evaluates whether long-horizon oil price forecasts are useful for upstream oil and gas investment planning. The stakeholder is an upstream planning team that must decide how to screen projects, how conservatively to price future cash flows, and whether public institutional outlooks can be used directly in capital allocation. We focus on the Energy Information Administration Annual Energy Outlook Brent price vintages because they provide the cleanest public long-horizon archive for a reproducible vintage evaluation.

The core analytical question is whether EIA long-term Brent forecasts add information relative to a naive no-change benchmark at horizons relevant to project screening and development timing. We evaluate three-year-ahead and five-year-ahead annual average Brent prices because those horizons align better with upstream appraisal, development sequencing, and final investment decisions than short-term spot forecasts do.

The project constructs a reproducible panel of EIA forecast vintages from 2013 through 2026, excluding 2024 because no AEO 2024 vintage was released. EIA forecasts are paired with realized annual Brent spot prices from FRED and converted into real 2025 dollars using CPI. Forecast performance is measured with mean error, mean percentage error, mean absolute error, root mean squared error, and mean absolute percentage error. The benchmark is a martingale-style no-change forecast equal to the most recently completed annual Brent price available at the forecast release date.

The main result is nuanced. EIA beats the martingale benchmark on RMSE at both horizons, with 3-year RMSE of 34.97 compared with 42.99 for the benchmark and 5-year RMSE of 34.32 compared with 47.34. At the same time, EIA forecasts are systematically optimistic: mean error is +20.44 dollars per barrel at three years and +26.64 at five years. A recursive historical bias correction improves accuracy, especially at the five-year horizon where RMSE falls to 25.36. Simple rolling autoregressive and futures-augmented models do not beat EIA in this implementation.

The recommendation is to use EIA as an informational baseline but not as a literal planning deck. The EIA series appears to contain useful information, so discarding it would be wasteful. However, the realized sample shows enough optimism that using the published forecast mechanically could overstate project value. A practical planning process should start from EIA, apply explicit conservative adjustment or bias correction, and document the adjustment so decision makers understand when the internal planning deck differs from the public institutional forecast.

## Scope and Stakeholder Context

The primary stakeholder is an upstream oil and gas company, especially strategy, planning, corporate finance, and new ventures teams. These teams rely on long-term commodity price assumptions when they screen exploration opportunities, evaluate project economics, compare capital allocation alternatives, and communicate assumptions to senior management. The report is also relevant to lenders, reserve-based financiers, private equity sponsors, and analysts who need to understand how much confidence to place in public long-term oil price outlooks.

The stakeholder’s decisions are not abstract statistical choices. They include whether a project advances past screening, whether a development case remains attractive under a standardized price deck, how much downside protection should be required before sanctioning capital, and whether an institutional public forecast can be adopted directly. A persistent positive bias in long-horizon oil forecasts can translate into overstated revenue, inflated NPV, optimistic IRR, and poor ranking of marginal projects. Conversely, if the institutional forecast contains information beyond a naive benchmark, discarding it can leave useful signal on the table.

This project therefore treats forecast evaluation as a decision-support exercise. The goal is not simply to identify a statistically elegant model. The goal is to determine whether a planning team should trust EIA long-term Brent forecasts, whether it should adjust them, and what type of adjustment is most defensible given public data and the limited realized sample.

## Research Questions

The report addresses five linked questions. First, do EIA long-horizon Brent forecasts contain useful information relative to a martingale no-change benchmark? Second, are the forecasts systematically biased, and if so, how large is the bias in both dollars per barrel and percentage terms? Third, can simple rolling econometric models outperform the institutional forecast? Fourth, does a recursive historical bias correction improve practical forecast performance without look-ahead bias? Fifth, does converting nominal and vintage-dollar quantities into real 2025 dollars create interpretive issues for the Brent analysis?

These questions are deliberately practical. The benchmark is transparent enough that a planning team could implement it without specialized modeling. The bias correction is simple enough to govern and explain. The rolling models test whether public price history and a front-month futures proxy can improve on institutional forecasts. The CPI diagnostic checks whether the real-dollar standardization supports comparability without becoming the driver of the substantive result.

## Data Sources and Coverage

The main forecast data source is EIA AEO Table 12, which contains petroleum price forecasts. The pipeline stores local raw workbooks for vintages 2013 through 2023, 2025, and 2026. AEO 2024 is excluded because that release does not exist in the archive. Each workbook is parsed for the Brent Spot row, the target-year columns, and the table’s constant-dollar base year. The code then maps each vintage into a common real 2025 dollar unit.

Realized annual Brent prices come from FRED series DCOILBRENTEU. Daily observations are averaged by calendar year. CPI comes from FRED series CPIAUCSL and is averaged to annual CPI for real-dollar conversion. The market-information extension uses Yahoo Finance Brent front-month futures ticker BZ=F. The World Bank commodity price forecast archive is included as supplementary material because it provides another public oil-price forecast history, although its object is crude oil average rather than exact Brent.

The realized evaluation sample contains 20 observations across the 3-year and 5-year horizons. This sample is necessarily small because long-horizon forecast evaluation requires target years to have already occurred. The small sample is a limitation, but it is also typical of vintage forecast evaluation in long-horizon energy planning. The report therefore emphasizes transparent metrics, robustness checks, and decision interpretation rather than overfitting a complex model.

## Data Processing and Unit Standardization

The first processing step is to turn heterogeneous vintage files into a structured panel. For each AEO vintage, the parser locates the year header row, identifies the Brent Spot row, records the table’s real-dollar base year, and stores one record for each vintage-target pair. The code preserves release dates so that benchmark and model features are aligned with information that would have been available at the time of forecast publication.

The second processing step converts all price series into real 2025 dollars. Annual CPI is computed from monthly CPI, and the conversion factor for each year equals the 2025 CPI average divided by that year’s CPI average. EIA forecasts reported in their table-dollar base year are multiplied by the corresponding base-year factor. Realized annual Brent prices are multiplied by the target-year factor. This standardization makes older and newer forecasts comparable in a common purchasing-power unit.

The third processing step builds the benchmark and evaluation panel. For each vintage-target pair, the forecast horizon is target year minus vintage year. The report keeps 3-year and 5-year observations with realized actuals. The martingale benchmark uses the latest completed annual Brent price available at the forecast origin, which is vintage year minus one. Forecast errors are defined as forecast minus actual, so positive mean error means the forecast is optimistic relative to realized Brent.

## Evaluation Metrics

The evaluation uses five metrics. Mean Error measures signed bias in dollars per barrel. Mean Percentage Error measures signed bias relative to realized price. Mean Absolute Error measures the typical absolute miss in dollars. Root Mean Squared Error penalizes large misses and is useful when extreme errors are especially damaging for project valuation. Mean Absolute Percentage Error measures typical percentage miss and helps compare accuracy across price regimes.

Using all five metrics matters because the stakeholder cares about two different properties: information and bias. A forecast can beat the benchmark on RMSE and still be too optimistic to use mechanically. That is exactly the main EIA finding. RMSE shows that EIA contains useful information beyond the no-change rule. ME and MPE show that this informational value does not eliminate the need for a planning haircut or governance adjustment.

The report avoids relying only on directional accuracy because the planning decision is fundamentally a level problem. Upstream economics depend on expected price levels over project-relevant years, not merely whether prices rise or fall. The report also avoids highly complex statistical tests because the realized long-horizon sample is small. Instead, it uses transparent forecast-error measures that are easy to audit in the GitHub appendix.

## Benchmark Results

The first result is that EIA beats the martingale benchmark on RMSE at both horizons. At the 3-year horizon, EIA RMSE is 34.97 compared with 42.99 for the martingale. At the 5-year horizon, EIA RMSE is 34.32 compared with 47.34. This indicates that EIA long-term forecasts contain information that is not captured by simply carrying forward the latest completed annual Brent price.

However, the same table shows substantial optimism. EIA mean error is +20.44 dollars per barrel at three years and +26.64 at five years. In percentage terms, this is +33.0 percent at three years and +36.5 percent at five years. For project valuation, that is economically large. A planning deck that systematically overshoots realized Brent by roughly one-third can materially change screening decisions and reported project attractiveness.

The martingale benchmark is also positively biased in this sample, but it is less accurate on RMSE. This pattern supports a balanced conclusion: the institutional forecast is better than a naive rule, but it still requires disciplined adjustment. A stakeholder should not interpret EIA’s RMSE advantage as permission to adopt the published forecast literally.

## Bias-Correction Results

The bias-correction exercise subtracts the historical mean EIA error within each horizon, estimated recursively using only prior realized errors. This design is important because it avoids look-ahead bias. For a given forecast origin, the correction uses only errors that would have been known at that time. The exercise therefore represents a feasible governance overlay rather than an ex post fitting exercise.

The correction improves RMSE modestly at three years and materially at five years. At three years, RMSE falls from 34.97 to 33.65. At five years, RMSE falls from 34.32 to 25.36 and MAPE falls to 23.5 percent. The correction is not perfect: it overcorrects the mean error into negative territory in the realized sample. Still, the performance gain demonstrates that historical optimism is not only descriptive; it is exploitable for practical planning.

For an upstream planning team, the implication is governance-oriented. The firm does not need to replace EIA with a complicated black-box model. A simple, documented, horizon-specific conservatism overlay can move the planning deck closer to realized performance. The exact haircut should be re-estimated as more vintages realize, but the principle is supported by the evidence.

## Rolling Model Results

The rolling econometric models test whether simple public-data models can improve on the institutional forecast. The Rolling AR model uses lagged annual real Brent prices. The Rolling AR plus Futures model adds release-month front-month Brent futures and a real basis proxy. Both models are estimated in expanding-window fashion so each forecast uses only prior information.

The models do not beat EIA in the current implementation. Rolling AR RMSE is 48.95 at the 3-year horizon and 51.24 at the 5-year horizon. Rolling AR plus Futures RMSE is 52.51 at three years and 53.23 at five years. These results do not mean market information is irrelevant. Rather, they show that a simple public front-month proxy is not enough to outperform the EIA long-horizon outlook in this sample.

This finding is useful because it prevents a common mistake: assuming that a reduced-form model is automatically better because it is data-driven. The EIA forecast may embed expert judgment, macro assumptions, supply-demand modeling, and policy expectations that are not captured by lagged annual Brent prices and front-month futures. The rolling models remain valuable as diagnostic baselines, but they should not replace the institutional forecast.

## CPI Diagnostic

One review concern was whether CPI conversion could distort the real Brent analysis. The project addresses this by computing CPI-Brent relationship diagnostics. Nominal Brent growth and CPI inflation are positively related, with correlation around 0.519. Real Brent growth and CPI inflation also remain positively related, with correlation around 0.476. The average gap between real-2025 and nominal annual Brent is about 23.63 dollars per barrel.

These diagnostics suggest that the CPI adjustment is not mechanically creating the main bias result. The conversion standardizes units across vintages and target years, but the substantive conclusion remains about forecast performance relative to realized Brent. In the report, the CPI conversion is best interpreted as a comparability tool rather than a causal model of oil prices.

The project nevertheless treats CPI as a limitation. Real-dollar analysis can improve comparability, but it may not match every stakeholder’s planning practice. Some companies evaluate nominal cash flows with explicit inflation assumptions. Others use real price decks for screening. The report’s real 2025 dollar approach is transparent and consistent, but users should adapt the unit convention to their valuation framework.

## Limitations

The first limitation is sample size. Long-horizon forecast evaluation is constrained by the need for realized target years. The 3-year and 5-year sample has only 20 observations across realized horizons. This limits formal inference and makes the estimates sensitive to large oil price shocks. The report therefore emphasizes transparent decision-oriented metrics instead of overstated statistical precision.

The second limitation is data availability. EIA provides a clean public archive, but other institutional forecasts are harder to integrate. IEA historical long-horizon Brent vintages were investigated but not included because the needed vintage-level series were not available in a clean public machine-readable panel within the project window. World Bank data are included as supplementary material, but the forecast object is crude oil average rather than exact Brent.

The third limitation is the futures extension. The project uses a public Brent front-month futures proxy rather than a full historical long-dated Brent futures strip. Long-horizon project economics would ideally use maturity-specific forward curve information. The current futures proxy is useful as a proof of concept but should not be interpreted as a definitive test of market-curve forecasting power.

The fourth limitation is that project-level cash-flow data are not included. The report evaluates forecasts, not project rankings. It can infer that optimistic forecasts may inflate NPV and IRR, but it cannot directly measure whether bias changes the ranking of specific projects under capital constraints. That would require a project-level panel with production profiles, cost assumptions, fiscal terms, and investment timing.

## Recommendations

First, stakeholders should continue using EIA as an informational baseline. The forecast beats the martingale benchmark on RMSE, which means it contains useful signal beyond a no-change rule. Discarding EIA would ignore a public institutional forecast that performs better than a simple carry-forward benchmark.

Second, stakeholders should not use EIA mechanically. The realized sample shows persistent optimistic bias. A planning team should treat the published EIA forecast as a starting point rather than the final internal price deck. The adjustment should be explicit, documented, and reviewed as new realized errors become available.

Third, the best current governance improvement is a horizon-specific bias overlay. A simple recursive historical correction improved 5-year performance substantially. The exact correction should be refined with additional vintages and stakeholder risk tolerance, but the principle is clear: forecast governance should account for historical optimism.

Fourth, rolling AR-style models should remain supplementary diagnostics. They can provide a transparent comparison and help challenge the planning deck, but they should not replace EIA in this version. Future work should test longer-dated futures curves and project-level valuation impacts before recommending a model-based replacement.

# Appendix A: Live GitHub Repository and File Map

