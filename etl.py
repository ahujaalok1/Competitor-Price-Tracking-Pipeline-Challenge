"""
etl.py
------
This script performs the Transformation + Load steps for the price tracking pipeline.

Steps:
1. Read today's raw scraped JSON (from scraper.py).
2. Read yesterday's cleaned JSON (if available).
3. Clean and standardize today's prices.
4. Compare today's and yesterday's prices → calculate price changes.
5. Save cleaned JSON for today's date.

Author: Alok Ahuja - Data Engineer
"""

import json, pathlib
from datetime import datetime, timezone, timedelta

# Define IST timezone (Amazon prices may differ across geographies, but we keep IST for consistency)
IST = timezone(timedelta(hours=5, minutes=30))

def load_json(path):
    """
    Utility function to safely load JSON files.
    Returns None if file not found (e.g., on first run when no yesterday file exists).
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def transform(today_data, yesterday_data):
    """
    Cleans and enriches today's data:
    - Ensures prices are floats.
    - Compares today's prices with yesterday's.
    - Adds price change (absolute + percentage).
    """
    results = []

    # Build dictionary for yesterday's prices for quick lookup
    yesterday_prices = {p["product_name"]: p["current_price"] for p in yesterday_data} if yesterday_data else {}

    for prod in today_data:
        price = prod.get("current_price")
        y_price = yesterday_prices.get(prod["product_name"])

        price_change = None
        pct_change = None

        # If both today and yesterday's price are available, compute change
        if price is not None and y_price is not None:
            price_change = round(price - y_price, 2)
            if y_price != 0:
                pct_change = round((price_change / y_price) * 100, 2)

        results.append({
            "product_name": prod["product_name"],
            "current_price": price,
            "currency": prod.get("currency", "USD"),
            "url": prod.get("url"),
            "source": prod.get("source"),
            "timestamp": prod.get("timestamp"),
            "price_change": price_change,        # Absolute change in price
            "price_change_pct": pct_change       # Percentage change in price
        })
    return results

if __name__ == "__main__":
    # Get today's and yesterday's dates
    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    yest_str = (datetime.now(IST) - timedelta(days=1)).strftime("%Y-%m-%d")

    # File paths
    pathlib.Path("data").mkdir(exist_ok=True)
    today_raw = f"data/raw_prices_{date_str}.json"
    yest_clean = f"data/prices_{yest_str}.json"
    today_clean = f"data/prices_{date_str}.json"

    # Load input data
    today_data = load_json(today_raw)
    yesterday_data = load_json(yest_clean)

    if not today_data:
        raise Exception(f"No data found for today: {today_raw}")

    # Apply transformations
    cleaned = transform(today_data, yesterday_data)

    # Save cleaned data to JSON
    with open(today_clean, "w") as f:
        json.dump(cleaned, f, indent=2)

    print(f"✅ ETL complete. Cleaned data saved → {today_clean}")
