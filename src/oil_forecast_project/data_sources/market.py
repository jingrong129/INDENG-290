from __future__ import annotations

import pandas as pd
import yfinance as yf

from oil_forecast_project.config import RAW_DIR


def fetch_brent_front_month_futures(start: str = "2010-01-01", end: str = "2026-12-31") -> pd.DataFrame:
    raw_path = RAW_DIR / "market" / "brent_front_month_futures_yahoo.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if raw_path.exists():
        data = pd.read_csv(raw_path, parse_dates=["date"])
    else:
        data = yf.download("BZ=F", start=start, end=end, auto_adjust=False, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0].lower().replace(" ", "_") for col in data.columns]
        else:
            data.columns = [str(col).lower().replace(" ", "_") for col in data.columns]
        data = data.reset_index().rename(columns={"Date": "date", "Adj Close": "adj_close"})
        data.columns = [str(col).lower() for col in data.columns]
        data["date"] = pd.to_datetime(data["date"])
        keep_cols = [col for col in ["date", "open", "high", "low", "close", "adj_close", "volume"] if col in data.columns]
        data = data[keep_cols].copy()
        data["close"] = pd.to_numeric(data["close"], errors="coerce")
        if "adj_close" not in data.columns:
            data["adj_close"] = data["close"]
        data.to_csv(raw_path, index=False)
    return data
