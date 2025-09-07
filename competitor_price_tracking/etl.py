"""
etl.py
------
Transformation + Load step for competitor price tracking.

Pipeline responsibilities:
1. Load today's raw scraped JSON from `data/raw_prices/`.
2. Load yesterday's cleaned JSON (if available).
3. Standardize and enrich today's data:
   - Ensure numeric prices.
   - Compute absolute and percentage price changes.
4. Save cleaned JSON into `data/cleaned_prices/`.

Author: Alok Ahuja
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

# Configuration

IST = timezone(timedelta(hours=5, minutes=30))
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw_prices"
CLEANED_DIR = Path(__file__).resolve().parent.parent / "data" / "cleaned_prices"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Utilities

def _load_json(path: Path) -> Optional[List[Dict[str, Any]]]:
    """Safely load JSON file, returning None if missing or invalid."""
    if not path.exists():
        logging.warning("File not found: %s", path)
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error("Failed to load JSON from %s: %s", path, e)
        return None


def _save_json(path: Path, data: Any) -> None:
    """Save data to JSON file with proper error handling."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logging.info("Saved cleaned data → %s", path)
    except Exception as e:
        logging.error("Failed to write JSON file %s: %s", path, e)
        raise

# Core transformation

def transform(today_data: List[Dict[str, Any]], yesterday_data: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Enrich today's scraped data by computing price deltas.
    """
    results: List[Dict[str, Any]] = []
    yesterday_prices = {p["product_name"]: p["current_price"] for p in yesterday_data} if yesterday_data else {}

    for prod in today_data:
        price = prod.get("current_price")
        y_price = yesterday_prices.get(prod["product_name"])

        price_change = None
        pct_change = None
        if price is not None and y_price is not None:
            price_change = round(price - y_price, 2)
            if y_price != 0:
                pct_change = round((price_change / y_price) * 100, 2)

        results.append(
            {
                "product_name": prod.get("product_name", "Unknown"),
                "current_price": price,
                "currency": prod.get("currency", "USD"),
                "url": prod.get("url"),
                "source": prod.get("source"),
                "timestamp": prod.get("timestamp"),
                "price_change": price_change,
                "price_change_pct": pct_change,
            }
        )

    return results

# Entrypoint

def run_etl(today: Optional[str] = None) -> Path:
    """
    Execute the ETL pipeline:
    - Load today's raw data
    - Load yesterday's cleaned data
    - Transform and save today's cleaned dataset

    Args:
        today (str): Optional date string (YYYY-MM-DD). Defaults to current IST date.

    Returns:
        Path: Path to the saved cleaned JSON file.
    """
    today_date = datetime.now(IST).strftime("%Y-%m-%d") if today is None else today
    yesterday_date = (datetime.now(IST) - timedelta(days=1)).strftime("%Y-%m-%d")

    today_raw = RAW_DIR / f"raw_prices_{today_date}.json"
    yesterday_clean = CLEANED_DIR / f"prices_{yesterday_date}.json"
    today_clean = CLEANED_DIR / f"prices_{today_date}.json"

    today_data = _load_json(today_raw)
    if not today_data:
        raise FileNotFoundError(f"No raw data found for today: {today_raw}")

    yesterday_data = _load_json(yesterday_clean)
    cleaned = transform(today_data, yesterday_data)
    _save_json(today_clean, cleaned)

    return today_clean


if __name__ == "__main__":
    run_etl()
