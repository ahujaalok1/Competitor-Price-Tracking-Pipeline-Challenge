"""
scraper.py
----------
Amazon product scraper for price tracking (multiple products).

Features:
1. Scrapes product name + price from a list of Amazon product URLs.
2. Falls back to mock price if scraping fails (blocked/dynamic content).
3. Cleans and converts price text into float.
4. Saves extracted data into a JSON file (raw format).
5. Each run saves a new file with the current date.

Author: Alok Ahuja - Data Engineer
"""

import requests
import random
import json
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0"
]

def _now_iso():
    return datetime.now(IST).isoformat()

def parse_price_text(txt):
    if not txt:
        return None
    clean = "".join(ch for ch in txt if ch.isdigit() or ch == '.')
    try:
        return float(clean)
    except ValueError:
        return None

# Pre-defined fallback values
FALLBACKS = {
    "B0FFTS7G7R": {"product_name": "Pixel 10", "current_price": 899.99, "currency": "USD"},
    "B0DLHLRDBY": {"product_name": "Samsung A16", "current_price": 299.99, "currency": "USD"},
    "B0F7K9LFCL": {"product_name": "Samsung Fold", "current_price": 1999.99, "currency": "USD"}
}

def scrape_product(url):
    headers = {
        "User-Agent": random.choice(UA_POOL),
        "Accept-Language": "en-US,en;q=0.9"
    }
    asin = url.rstrip('/').split('/')[-1]
    fallback = FALLBACKS.get(asin, {})
    timestamp = _now_iso()

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        name_el = soup.find("span", {"id": "productTitle"})
        product_name = name_el.get_text(strip=True) if name_el else fallback.get("product_name", "Unknown Product")

        price_el = (
            soup.find("span", {"id": "priceblock_ourprice"}) or
            soup.find("span", {"id": "priceblock_dealprice"}) or
            soup.find("span", {"class": "a-price-whole"}) or
            soup.find("span", {"class": "a-offscreen"})
        )

        if price_el and price_el.get_text(strip=True):
            raw_price = price_el.get_text().strip()
            price = parse_price_text(raw_price)
            currency = ("USD" if "$" in raw_price else
                        "INR" if "₹" in raw_price else
                        "GBP" if "£" in raw_price else
                        fallback.get("currency", "USD"))
            return {
                "product_name": product_name,
                "current_price": price,
                "currency": currency,
                "url": url,
                "source": "amazon",
                "timestamp": timestamp
            }
        else:
            raise ValueError("Price not found in HTML")

    except Exception as e:
        return {
            "product_name": fallback.get("product_name", "Unknown Product"),
            "current_price": fallback.get("current_price", 0.0),
            "currency": fallback.get("currency", "USD"),
            "url": url,
            "source": "amazon_mock",
            "timestamp": timestamp,
            "note": f"Fallback due to error: {e}"
        }

def main():
    PRODUCT_URLS = [
        "https://www.amazon.com/dp/B0FFTS7G7R",   # Pixel 10
        "https://www.amazon.com/dp/B0F7K9LFCL",   # Samsung Fold
        "https://www.amazon.com/dp/B0DLHLRDBY",   # Samsung A16
    ]

    results = [scrape_product(url) for url in PRODUCT_URLS]

    # Define and ensure the output directory
    script_dir = Path(__file__).parent.resolve()
    data_dir = script_dir / "data"
    data_dir.mkdir(exist_ok=True)

    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    out_path = data_dir / f"raw_prices_{date_str}.json"

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Scraping complete. Saved data → {out_path}")
    except (IOError, TypeError) as e:
        print(f"Error writing JSON file: {e}")

    for item in results:
        print(item)

if __name__ == "__main__":
    main()
