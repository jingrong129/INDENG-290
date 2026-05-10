---
title: "Improving Long-Term Oil Price Forecasts"
subtitle: "Final Project Report"
author:
  - "Zhangrui Ji"
  - "Jinrong Yan"
  - "Dahai Huang"
  - "Jingyue Shao"
date: "May 11, 2026"
geometry: margin=1in
fontsize: 11pt
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - |
    \usepackage{float}
  - |
    \usepackage{booktabs}
  - |
    \usepackage{longtable}
  - |
    \usepackage{array}
  - |
    \setlength{\parskip}{0.5em}
    \setlength{\parindent}{0pt}
---

\thispagestyle{empty}

\begin{center}
{\LARGE \textbf{Improving Long-Term Oil Price Forecasts}}\\[1.2em]
{\Large Final Project Report}\\[2.0em]

{\large Team Members}\\[0.6em]
Zhangrui Ji\\
Jinrong Yan\\
Dahai Huang\\
Jingyue Shao\\[2.0em]

{\large UCB Energy Project}\\[0.6em]
May 11, 2026
\end{center}

\newpage

# Executive Summary

This project evaluates whether long-horizon oil price forecasts are decision-useful for upstream oil and gas investment planning. The primary stakeholder is an upstream firm or planning team that must decide which projects to screen, how conservatively to price future cash flows, and whether institutional long-term price decks can be used directly in capital allocation. We focus on the EIA Annual Energy Outlook (AEO) Brent forecast vintages because they provide the cleanest publicly accessible long-horizon archive. The core analytical question is whether these forecasts add information relative to a naive no-change benchmark at horizons that matter for project screening and development timing, especially three-year-ahead and five-year-ahead annual average Brent prices.

Methodologically, the project constructs a reproducible vintage evaluation panel. EIA forecast vintages from 2013 to 2026 are paired with realized annual average Brent spot prices from FRED. Both forecasts and realizations are converted into real 2025 U.S. dollars using CPI so that forecast performance is measured on a consistent basis across vintages. We compare EIA forecasts with a martingale benchmark equal to the most recently completed annual Brent price available at the forecast release date. We then test two out-of-sample model extensions, a rolling autoregressive model and a rolling autoregressive model augmented with Brent front-month futures, and we also estimate a bias-corrected EIA series using only prior realized forecast errors to avoid look-ahead bias.

The main results are threefold. First, EIA forecasts outperform the martingale benchmark in RMSE at both horizons. For the three-year horizon, EIA RMSE is 34.97 versus 42.99 for the benchmark. For the five-year horizon, EIA RMSE is 34.32 versus 47.34. Second, EIA forecasts are clearly optimistic in level terms and percentage terms. Mean error is +20.44 dollars per barrel at three years and +26.64 at five years, while mean percentage error is +33.0 percent and +36.5 percent, respectively. Third, a simple expanding-window bias correction improves forecast accuracy, especially at five years where RMSE falls to 25.36 and MAPE falls to 23.5 percent. The rolling econometric models do not outperform EIA in the current implementation.

Our recommendation is that stakeholders should treat EIA long-term Brent forecasts as informative but not literal. The EIA series appears more useful than a naive carry-forward rule, so it remains a valuable planning input. However, using it mechanically is risky because the realized sample shows systematic optimism. In practice, the best current guidance from this project is to use EIA as a baseline, apply explicit conservatism or bias adjustment in project valuation, and avoid assuming that a simple reduced-form time-series model will necessarily improve on the institutional outlook.

# Scope

## Stakeholder

The primary stakeholder is an upstream oil and gas company, especially the planning, strategy, corporate finance, and new ventures teams that rely on long-term commodity price assumptions for project screening and capital allocation. The report is also relevant to banks, reserve-based lenders, and private equity sponsors that must assess project economics under long-horizon oil price uncertainty.

## Stakeholder Decisions

The stakeholder must make several linked decisions:

- Which projects should advance past screening and into more detailed evaluation.
- Whether a project remains attractive once a standardized and conservative oil price deck is applied.
- How much confidence to place in institutional long-term oil outlooks when estimating NPV, IRR, and payback.
- Whether a firm should adopt a simple internal adjustment rule to counteract historical optimism in public long-term forecasts.

## Focus Questions

This project addresses five questions:

1. Do EIA long-horizon Brent forecasts contain useful information relative to a naive martingale benchmark?
2. Are these forecasts systematically biased, and if so, by how much in both dollar and percentage terms?
3. Can simple rolling econometric models outperform the institutional forecast?
4. Does a historical bias correction improve practical forecasting performance without introducing look-ahead bias?
5. Does the CPI-based conversion to real 2025 dollars create interpretive issues for the underlying Brent price analysis?

# Methodology

## Performance Metrics

We evaluate forecast performance with five metrics:

- Mean Error (ME): average signed forecast error in real 2025 dollars per barrel. This captures optimism or pessimism directly.
- Mean Percentage Error (MPE): average signed error scaled by the realized price. This shows whether bias is economically large in percentage terms.
- Mean Absolute Error (MAE): average absolute miss in dollars per barrel.
- Root Mean Squared Error (RMSE): square-root average of squared misses, which penalizes large errors more heavily and is useful when extreme forecasting mistakes are especially costly.
- Mean Absolute Percentage Error (MAPE): average absolute miss scaled by the realized price.

These metrics are appropriate because the stakeholder cares about both directional bias and forecast accuracy. ME and MPE matter for project valuation because a persistent positive bias can systematically inflate expected cash flows. RMSE and MAE matter because project teams also need a sense of the typical forecast miss in level terms. We considered relying only on RMSE, but that would have obscured the most decision-relevant finding: EIA can beat the naive benchmark on RMSE while still being systematically optimistic. We also considered a directional accuracy metric and Theil-style relative statistics, but with a small realized sample and a level-forecasting problem, the chosen metrics were more transparent for stakeholder interpretation.

## Pipeline Design

The pipeline is fully reproducible and implemented in Python. It ingests public data, standardizes units and dates, builds an evaluation panel, computes benchmark and model metrics, and writes processed data plus graphics for downstream use.

![Pipeline flowchart](outputs/report_pipeline_flowchart.png){ width=95% }

The main processing steps are:

1. Download and parse EIA AEO Table 12 Brent forecast vintages.
2. Download FRED Brent spot and CPI series and construct annual realized Brent prices.
3. Convert forecasts and realizations to real 2025 dollars.
4. Build release-month market features from front-month Brent futures.
5. Construct the 3-year and 5-year evaluation panel.
6. Compare EIA with a martingale benchmark.
7. Estimate rolling out-of-sample models and a bias-corrected EIA series.
8. Export CSV files, figures, an Excel workbook, and summary materials.

## Analytical Design

### Forecasted Quantity

The forecast object is annual average Brent spot price. The unit used in the core analysis is real 2025 U.S. dollars per barrel. We focus on horizons of three years ahead and five years ahead because these better match the timescale of upstream project screening, appraisal, development sequencing, and final investment decisions than short-term spot forecasting does.

### Evaluation Logic

For each EIA vintage year, we pair the forecast for a future target year with the realized annual average Brent price for that target year. We then calculate realized forecast errors only where the actual target year is already observed. This produces a realized evaluation sample of 20 forecast observations across the 3-year and 5-year horizons, drawn from 11 EIA publication years.

The naive benchmark is a martingale or no-change forecast. At release date, the benchmark forecast for every future horizon equals the latest completed annual Brent average already observed. We use the term martingale benchmark rather than random walk because the forecasting rule is “future expected value equals current observed level,” not “future level follows a drifted path.”

We also estimate two out-of-sample rolling models:

- Rolling AR: linear regression on lagged annual real Brent prices.
- Rolling AR + Futures: the same core lag structure with a release-month futures level and real basis term.

Both rolling models are estimated with an expanding window. Each forecast uses only information available before the origin year being predicted. The bias-corrected EIA forecast is also estimated recursively: for a given horizon, the correction uses only the mean realized EIA forecast error from earlier vintages. This prevents look-ahead bias.

### Tradeoffs and Design Choices

Several design tradeoffs shaped the final implementation:

- We centered the analysis on EIA rather than IEA because EIA vintages are publicly accessible and machine-readable, while historical IEA long-horizon Brent vintages were not available in a clean panel during the project window.
- We use annual average Brent rather than monthly prices because annual averages align better with long-horizon project planning and the AEO forecast object.
- We supplement the EIA analysis with World Bank data, but do not merge it into the main benchmark table because the World Bank series is “Crude oil, avg,” not exact Brent.
- We use front-month Brent futures as a public market-information proxy, recognizing that this is weaker than a full long-dated historical Brent curve.
- We evaluate in real 2025 dollars to maintain intertemporal comparability, while separately diagnosing whether the CPI conversion changes interpretation materially.

# Data

## Evolution of the Data Search

The project began with a broad objective: compare institutional long-term oil forecasts with realized outcomes at project-relevant horizons. That required three types of data: forecast vintages, realized Brent prices, and a transparent inflation series for unit conversion. We initially explored several institutional sources, including the EIA, the IEA, and the World Bank. The EIA archive proved to be the most workable because its AEO Table 12 releases contain a consistent long-horizon petroleum price table that can be parsed programmatically across years.

We also searched for additional market information to support model extensions and selected Brent front-month futures as a public proxy that could be integrated quickly. Several data elements were sought but not obtained in sufficiently usable form. These include a clean machine-readable panel of historical IEA long-horizon Brent forecasts, a historical long-dated Brent futures strip by maturity, and project-level NPV or IRR data that would allow direct testing of whether forecast bias changes the relative ranking of projects.

## Data Obtained

The analysis uses the following data:

- **EIA AEO Table 12 Brent Spot forecasts** for vintages 2013 through 2026, excluding 2024 because no AEO 2024 vintage exists in the archive. Source pages: <https://www.eia.gov/outlooks/aeo/tables_ref.php> and <https://www.eia.gov/outlooks/archive/>.
- **FRED Brent spot series** `DCOILBRENTEU` for realized spot prices: <https://fred.stlouisfed.org/series/DCOILBRENTEU>.
- **FRED CPI series** `CPIAUCSL` for inflation adjustment: <https://fred.stlouisfed.org/series/CPIAUCSL>.
- **Yahoo Finance Brent futures** ticker `BZ=F`, accessed through `yfinance`: <https://finance.yahoo.com/quote/BZ=F/history>.
- **World Bank commodity forecast archive** for supplementary oil forecasts: <https://www.worldbank.org/en/research/commodity-markets/price-forecasts>.

The realized evaluation sample contains 11 EIA publication years and 20 forecast observations across the 3-year and 5-year horizons.

## Data Handling

The data handling process is designed to preserve comparability across vintages:

- EIA Table 12 values are read from each vintage workbook and mapped to their reported constant-dollar base year.
- Annual average CPI is computed from monthly CPI and used to convert every forecast vintage into real 2025 dollars.
- Daily Brent spot prices from FRED are aggregated to annual averages and deflated to real 2025 dollars using the same CPI framework.
- Release-month features are built by averaging spot and futures prices within the EIA publication month.
- Forecast horizons are defined as `target_year - vintage_year`, and only 3-year and 5-year realized observations are retained for the main benchmark panel.

The main processed datasets are stored in the repository under `data/processed/`, and the reproducible pipeline exports a consolidated workbook to `outputs/analysis_outputs.xlsx`.

## Live Links to the Data Repository

- Project data repository root: <https://github.com/jingrong129/INDENG-290/tree/main/data>
- Processed data directory: <https://github.com/jingrong129/INDENG-290/tree/main/data/processed>
- Raw EIA archive files in repo: <https://github.com/jingrong129/INDENG-290/tree/main/data/raw/eia>

# Results and Findings

## Results

### 1. EIA beats the naive benchmark on RMSE

The first key result is that EIA forecasts outperform the martingale benchmark on RMSE at both horizons. This means the EIA outlook contains useful information beyond simply carrying the latest completed annual Brent average forward.

| Model | Horizon | N | ME | MPE | MAE | RMSE | MAPE |
|---|---:|---:|---:|---:|---:|---:|---:|
| EIA | 3y | 11 | 20.44 | 0.330 | 26.01 | 34.97 | 0.388 |
| Martingale | 3y | 11 | 17.25 | 0.276 | 31.66 | 42.99 | 0.438 |
| EIA | 5y | 9 | 26.64 | 0.365 | 28.09 | 34.32 | 0.381 |
| Martingale | 5y | 9 | 13.79 | 0.248 | 38.90 | 47.34 | 0.512 |

![Benchmark comparison](outputs/benchmark_metrics.png){ width=85% }

### 2. EIA forecasts are systematically optimistic

The second key result is that EIA’s informational value does not remove its bias problem. Mean error is strongly positive at both horizons, and the percentage bias is economically large. A mean percentage error of roughly one-third means that the EIA forecast tends to overshoot realized Brent by about 33 percent at the three-year horizon and 36 percent at the five-year horizon in the realized sample.

![EIA forecast vintages versus realized Brent](outputs/eia_vintages_vs_actual.png){ width=92% }

### 3. Simple bias correction improves performance, especially at five years

We estimated a recursive bias correction by subtracting the historical mean realized EIA error within each horizon, using only earlier vintages. This out-of-sample correction lowers RMSE from 34.97 to 33.65 at three years and from 34.32 to 25.36 at five years. It also reduces MAPE materially, especially at five years.

| Model | Horizon | N | ME | MPE | MAE | RMSE | MAPE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bias-Corrected EIA | 3y | 10 | -27.93 | -0.315 | 29.26 | 33.65 | 0.341 |
| Bias-Corrected EIA | 5y | 8 | -19.33 | -0.212 | 20.53 | 25.36 | 0.235 |

The correction is not perfect because it appears to overcorrect in the current sample, flipping mean error from positive to negative. Still, the exercise shows that historical bias is exploitable and therefore relevant for practical decision rules.

![Bias correction metrics](outputs/bias_correction_metrics.png){ width=90% }

### 4. Rolling econometric models do not beat EIA in the current implementation

The rolling autoregressive models provide a useful baseline, but they do not improve on the institutional forecast in the current design. The best rolling model RMSE remains above the EIA RMSE at both horizons. This suggests that the EIA outlook embeds information not captured by the simple reduced-form public-data models tested here.

| Model | Horizon | N | ME | MPE | MAE | RMSE | MAPE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Rolling AR | 3y | 26 | 10.13 | 0.157 | 35.33 | 48.95 | 0.447 |
| Rolling AR | 5y | 24 | -5.41 | -0.019 | 35.95 | 51.24 | 0.379 |
| Rolling AR + Futures | 3y | 9 | 17.96 | 0.325 | 40.11 | 52.51 | 0.549 |
| Rolling AR + Futures | 5y | 7 | 7.57 | 0.244 | 36.61 | 53.23 | 0.539 |

![Rolling model RMSE](outputs/rolling_model_rmse.png){ width=82% }

### 5. CPI adjustment does not overturn the substantive conclusion

One concern raised during project review was whether the relationship between CPI and Brent could distort the real-price series used as the foundation of the analysis. We tested this directly. Nominal Brent growth and CPI inflation are positively related, but the relationship remains of similar magnitude after converting Brent into real terms. This suggests the CPI deflation step is not mechanically generating the bias result; it is mainly standardizing the unit of measurement.

Key diagnostics:

- Correlation between nominal Brent growth and CPI inflation: 0.519
- Correlation between real Brent growth and CPI inflation: 0.476
- Average difference between nominal and real-2025 annual Brent: 23.63 dollars per barrel

![CPI and Brent relationship](outputs/cpi_brent_relationship.png){ width=92% }

## Findings

The findings are most useful when translated back into the stakeholder’s decision context.

First, EIA long-horizon forecasts are not useless. They outperform a transparent no-change benchmark, which means they capture information relevant to future annual Brent prices. For a planning team, that matters because it justifies continuing to monitor institutional outlooks rather than replacing them with a trivial internal rule.

Second, the optimistic bias is large enough to matter economically. If an upstream firm were to use these forecasts mechanically in project economics, the likely consequence would be overstated revenue assumptions and inflated NPV or IRR, especially for projects whose economics are strongly levered to oil price levels.

Third, the project suggests that a practical governance improvement is feasible. Even a simple recursive bias adjustment materially improves performance at five years. That does not mean the exact correction estimated here should be adopted without refinement, but it does show that “use EIA, but haircut it systematically” is better aligned with realized performance than “use EIA as published.”

Fourth, the current rolling AR and futures-augmented models should not replace the institutional forecast. They are best interpreted as diagnostic baselines showing that simple public-data models do not automatically beat the EIA on long-horizon planning tasks.

# Recommendations

We recommend the following to the stakeholder:

1. Use the EIA long-term Brent forecast as an informational baseline rather than discarding it altogether.
2. Do not use the published EIA level forecast mechanically in project valuation, because the realized sample shows persistent optimistic bias.
3. Apply an explicit conservative adjustment or bias-correction overlay when converting institutional forecasts into planning price decks.
4. Prioritize governance and documentation of price-deck adjustments so that project teams understand when the planning deck differs from the raw institutional forecast.
5. Treat simple rolling AR-style models as supplementary diagnostics, not as replacements for institutional long-horizon outlooks.
6. As future work, integrate a longer-horizon market curve or project-level valuation panel if the goal is to test whether bias changes the relative ranking of projects under capital constraints.

# Appendix

## A. Live Link to Code Repository

- GitHub repository: <https://github.com/jingrong129/INDENG-290>
- Source code directory: <https://github.com/jingrong129/INDENG-290/tree/main/src>

## B. Live Link to Data Repository

- Data directory: <https://github.com/jingrong129/INDENG-290/tree/main/data>
- Processed data directory: <https://github.com/jingrong129/INDENG-290/tree/main/data/processed>
- Benchmark metrics CSV: <https://github.com/jingrong129/INDENG-290/blob/main/data/processed/benchmark_metrics.csv>
- Bias-corrected metrics CSV: <https://github.com/jingrong129/INDENG-290/blob/main/data/processed/bias_corrected_metrics.csv>
- Rolling-model metrics CSV: <https://github.com/jingrong129/INDENG-290/blob/main/data/processed/rolling_model_metrics.csv>

## C. Live Links to Supplementary Analytics

- Summary output: <https://github.com/jingrong129/INDENG-290/blob/main/outputs/project_summary.md>
- Output directory index: <https://github.com/jingrong129/INDENG-290/tree/main/outputs>

## D. Repository Paths Used in This Submission

- Main report source: `reports/final_project_report.md`
- Flowchart generator: `scripts/generate_report_flowchart.py`
- Main pipeline entry point: `scripts/run_pipeline.py`
- Processed benchmark metrics: `data/processed/benchmark_metrics.csv`
- Bias-corrected metrics: `data/processed/bias_corrected_metrics.csv`
