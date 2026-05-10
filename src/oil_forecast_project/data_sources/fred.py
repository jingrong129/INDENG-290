from __future__ import annotations

from urllib.parse import urlencode

import pandas as pd

from oil_forecast_project.config import RAW_DIR


FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def _fred_csv_url(series_id: str) -> str:
    return f"{FRED_GRAPH_URL}?{urlencode({'id': series_id})}"


def fetch_fred_series(series_id: str, date_col: str = "DATE", value_col: str | None = None) -> pd.DataFrame:
    url = _fred_csv_url(series_id)
    raw_path = RAW_DIR / "fred" / f"{series_id}.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if raw_path.exists():
        df = pd.read_csv(raw_path)
    else:
        df = pd.read_csv(url)
        df.to_csv(raw_path, index=False)
    if date_col not in df.columns:
        date_col = df.columns[0]
    if value_col is None:
        value_col = df.columns[1]
    df = df.rename(columns={date_col: "date", value_col: "value"})
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.assign(series_id=series_id)


def fetch_brent_spot_daily() -> pd.DataFrame:
    return fetch_fred_series("DCOILBRENTEU")


def fetch_cpi_monthly() -> pd.DataFrame:
    return fetch_fred_series("CPIAUCSL")
