from __future__ import annotations

import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

from oil_forecast_project.config import RAW_DIR


WORLD_BANK_FORECAST_ARCHIVE = "https://www.worldbank.org/en/research/commodity-markets/price-forecasts"


def fetch_world_bank_oil_average_forecasts(start_year: int = 2019, end_year: int = 2025) -> pd.DataFrame:
    raw_path = RAW_DIR / "world_bank" / "oil_average_forecasts.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if raw_path.exists():
        return pd.read_csv(raw_path, parse_dates=["release_date"])

    html = requests.get(WORLD_BANK_FORECAST_ARCHIVE, timeout=60).text
    soup = BeautifulSoup(html, "html.parser")
    links: list[tuple[str, str]] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "Forecast" not in href and "forecast" not in href:
            continue
        match = re.search(r"(20\d{2})", href)
        if not match:
            continue
        vintage_year = int(match.group(1))
        if not start_year <= vintage_year <= end_year:
            continue
        links.append((href, anchor.get_text(strip=True) or "Unknown"))

    records: list[dict[str, object]] = []
    seen_urls: set[str] = set()
    for href, month_text in links:
        if href in seen_urls or not href.lower().endswith((".xlsx", ".xls")):
            continue
        seen_urls.add(href)
        vintage_year = int(re.search(r"(20\d{2})", href).group(1))
        release_month = (month_text[:3] or "Jan").title()
        release_date = pd.to_datetime(f"{release_month} 1, {vintage_year}", errors="coerce")
        frame = pd.read_excel(href, sheet_name=0, header=None)

        mask = frame.astype(str).apply(lambda col: col.str.contains("Crude oil, avg", case=False, na=False)).any(axis=1)
        if not mask.any():
            continue
        row = frame.loc[mask].iloc[0]
        header_row_idx = max(mask[mask].index[0] - 3, 0)
        years = frame.iloc[header_row_idx]
        for col_idx, year_value in enumerate(years):
            if pd.isna(year_value):
                continue
            try:
                target_year = int(year_value)
            except (TypeError, ValueError):
                continue
            if target_year < 1900 or target_year > 2100:
                continue
            forecast = pd.to_numeric(row.iloc[col_idx], errors="coerce")
            if pd.isna(forecast):
                continue
            records.append(
                {
                    "provider": "WorldBank",
                    "price_definition": "Crude oil, avg",
                    "vintage_year": vintage_year,
                    "release_date": release_date,
                    "target_year": target_year,
                    "forecast_nominal_usd_per_bbl": float(forecast),
                    "source_url": href,
                }
            )

    df = pd.DataFrame.from_records(records).sort_values(["vintage_year", "target_year"]).reset_index(drop=True)
    df.to_csv(raw_path, index=False)
    return df
