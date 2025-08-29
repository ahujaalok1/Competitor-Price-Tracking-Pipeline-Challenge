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

import json
import pandas as pd
from datetime import datetime
import pathlib

# Define data directory
DATA_DIR = pathlib.Path("data")

def process_day(raw_file, prev_day_data):
    """Process one day's raw file into cleaned format with price changes."""
    today_str = raw_file.stem.split("_")[-1]  # extract date from filename
    today_date = datetime.strptime(today_str, "%Y-%m-%d").date()

    # Load raw data
    with open(raw_file, "r") as f:
        raw_data = json.load(f)

    cleaned_data = []
    for record in raw_data:
        price = float(record["current_price"]) if record["current_price"] else None

        # Default changes
        price_change = None
        price_change_pct = None

        # Compare with previous day if exists
        if prev_day_data is not None:
            prev_record = next(
                (r for r in prev_day_data if r["product_name"] == record["product_name"]), 
                None
            )
            if prev_record and prev_record["current_price"] is not None and price is not None:
                prev_price = float(prev_record["current_price"])
                price_change = round(price - prev_price, 2)
                if prev_price > 0:
                    price_change_pct = round((price - prev_price) / prev_price * 100, 2)

        cleaned_data.append({
            **record,
            "current_price": price,
            "price_change": price_change,
            "price_change_pct": price_change_pct
        })

    # Save cleaned file
    output_file = DATA_DIR / f"prices_{today_date}.json"
    with open(output_file, "w") as f:
        json.dump(cleaned_data, f, indent=2)

    print(f"Processed {raw_file.name} → {output_file.name}")
    return cleaned_data


def main():
    # Loop through all raw files sorted by date
    raw_files = sorted(DATA_DIR.glob("raw_prices_*.json"))
    prev_day_data = None

    for raw_file in raw_files:
        prev_day_data = process_day(raw_file, prev_day_data)


if __name__ == "__main__":
    main()

