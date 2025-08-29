"""
scraper.py
----------
This script performs the Extraction step for the price tracking pipeline.

Steps:
1. Send a request to Amazon search results page for "iPhone 14".
2. Parse the HTML to extract the first product name + price.
3. If scraping fails (blocked / no price found), use a fallback mock price.
4. Save the extracted data into a JSON file (raw format).
5. Each run saves a new file with the current date.

Author: Alok Ahuja - Data Engineer
"""

import requests, random, json, pathlib, time
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# Timezone: IST (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# User-Agent pool for mimicking real browsers (helps reduce blocking)
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]

def _now_iso():
    return datetime.now(IST).isoformat()

def parse_price_text(txt):
    """Convert price string like '1,199.99' → float"""
    if not txt:
        return None
    clean = "".join(ch for ch in txt if ch.isdigit() or ch in ".")
    try:
        return float(clean)
    except:
        return None

def scrape_iphone14():
    """Scrape Amazon for iPhone 14 price (first search result)."""
    url = "https://www.amazon.com/s?k=iPhone+14"
    headers = {"User-Agent": random.choice(UA_POOL)}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            raise Exception(f"Status {resp.status_code}")
    except Exception as e:
        # Fallback: return mock if scraping fails
        return {
            "product_name": "iPhone 14",
            "current_price": 799.99,   # Mock value
            "currency": "USD",
            "url": url,
            "source": "amazon_mock",
            "timestamp": _now_iso()
        }

    soup = BeautifulSoup(resp.text, "html.parser")

    name_el = soup.select_one("h2 a.a-link-normal")
    price_whole = soup.select_one("span.a-price-whole")
    price_frac = soup.select_one("span.a-price-fraction")

    price = None
    if price_whole:
        price = parse_price_text(price_whole.get_text() + "." + (price_frac.get_text() if price_frac else "00"))

    return {
        "product_name": name_el.get_text(strip=True) if name_el else "iPhone 14",
        "current_price": price,
        "currency": "USD",
        "url": url,
        "source": "amazon",
        "timestamp": _now_iso()
    }

if __name__ == "__main__":
    data = [scrape_iphone14()]

    pathlib.Path("data").mkdir(exist_ok=True)
    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    out_path = f"data/raw_prices_{date_str}.json"

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Scraping complete. Saved iPhone 14 data → {out_path}")
