"""
scraper.py
-----------
Amazon product scraper for competitor price tracking.

Responsibilities:
1. Scrape product name + price from a list of Amazon product URLs.
2. Fall back to mock prices if scraping fails (blocked/dynamic content).
3. Save raw scraped data into JSON files under `data/raw_prices/`.

Author: Alok Ahuja
"""

from __future__ import annotations

import json
import logging
import random
import requests
from pathlib import Path
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# Configuration

IST = timezone(timedelta(hours=5, minutes=30))
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw_prices"

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
]

PRODUCT_URLS = [
    "https://www.amazon.com/dp/B0FFTS7G7R",  # Pixel 10 Pro
    "https://www.amazon.com/dp/B0F7K9LFCL",  # Samsung Fold
    "https://www.amazon.com/dp/B0DLHLRDBY",  # Samsung A16
]

# Mock fallback values (in case scraping fails)
FALLBACKS: Dict[str, Dict[str, Any]] = {
    "B0FFTS7G7R": {"product_name": "Pixel 10 Pro", "current_price": 899.99, "currency": "USD"},
    "B0DLHLRDBY": {"product_name": "Samsung A16", "current_price": 299.99, "currency": "USD"},
    "B0F7K9LFCL": {"product_name": "Samsung Fold", "current_price": 1999.99, "currency": "USD"},
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Helpers

def _now_iso() -> str:
    """Return current IST timestamp in ISO format."""
    return datetime.now(IST).isoformat()


def _parse_price_text(raw: str) -> float | None:
    """Extract numeric value from price string."""
    clean = "".join(ch for ch in raw if ch.isdigit() or ch == ".")
    try:
        return float(clean)
    except ValueError:
        return None

# Core Scraper

def scrape_product(url: str) -> Dict[str, Any]:
    """Scrape a single Amazon product page."""
    asin = url.rstrip("/").split("/")[-1]
    fallback = FALLBACKS.get(asin, {})
    timestamp = _now_iso()

    headers = {
        "User-Agent": random.choice(UA_POOL),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        name_el = soup.find("span", {"id": "productTitle"})
        product_name = name_el.get_text(strip=True) if name_el else fallback.get("product_name", "Unknown Product")

        price_el = (
            soup.find("span", {"id": "priceblock_ourprice"})
            or soup.find("span", {"id": "priceblock_dealprice"})
            or soup.find("span", {"class": "a-price-whole"})
            or soup.find("span", {"class": "a-offscreen"})
        )

        if price_el and price_el.get_text(strip=True):
            raw_price = price_el.get_text().strip()
            price = _parse_price_text(raw_price)
            currency = (
                "USD"
                if "$" in raw_price
                else "INR"
                if "₹" in raw_price
                else "GBP"
                if "£" in raw_price
                else fallback.get("currency", "USD")
            )

            return {
                "product_name": product_name,
                "current_price": price,
                "currency": currency,
                "url": url,
                "source": "amazon",
                "timestamp": timestamp,
            }

        raise ValueError("Price not found in HTML")

    except Exception as e:
        logging.warning("Falling back for %s due to error: %s", asin, e)
        return {
            "product_name": fallback.get("product_name", "Unknown Product"),
            "current_price": fallback.get("current_price", 0.0),
            "currency": fallback.get("currency", "USD"),
            "url": url,
            "source": "amazon_mock",
            "timestamp": timestamp,
            "note": f"Fallback due to error: {e}",
        }

# Entrypoint

def run_scraper(urls: List[str] | None = None) -> Path:
    """
    Run the scraper for a list of product URLs.
    Saves results into a dated JSON file in data/raw_prices/.
    Returns the path to the saved file.
    """
    urls = urls or PRODUCT_URLS
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    results = [scrape_product(url) for url in urls]
    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    out_path = DATA_DIR / f"raw_prices_{date_str}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logging.info("Scraping complete. Saved %d products → %s", len(results), out_path)
    return out_path


if __name__ == "__main__":
    run_scraper()
