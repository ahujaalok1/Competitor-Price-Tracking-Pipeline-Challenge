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

import requests, random, json, pathlib
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# Timezone: IST (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# User-Agent pool to mimic real browsers (helps reduce blocking)
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0"
]

def _now_iso():
    return datetime.now(IST).isoformat()

def parse_price_text(txt):
    """Convert price string like '$1,199.99' → float"""
    if not txt:
        return None
    clean = "".join(ch for ch in txt if ch.isdigit() or ch in ".")
    try:
        return float(clean)
    except:
        return None

def scrape_product(url, fallback_name="Unknown Product", fallback_price=0.0, fallback_currency="USD"):
    """Scrape Amazon product page for name + price."""
    headers = {
        "User-Agent": random.choice(UA_POOL),
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            raise Exception(f"Status {resp.status_code}")
    except Exception:
        # Fallback: return mock data
        return {
            "product_name": fallback_name,
            "current_price": fallback_price,
            "currency": fallback_currency,
            "url": url,
            "source": "amazon_mock",
            "timestamp": _now_iso()
        }

    soup = BeautifulSoup(resp.text, "html.parser")

    # Product name
    name_el = soup.find("span", {"id": "productTitle"})
    product_name = name_el.get_text(strip=True) if name_el else fallback_name

    # Price (Amazon uses multiple selectors)
    price_el = (
        soup.find("span", {"id": "priceblock_ourprice"}) or
        soup.find("span", {"id": "priceblock_dealprice"}) or
        soup.find("span", {"class": "a-price-whole"}) or
        soup.find("span", {"class": "a-offscreen"})
    )

    price = parse_price_text(price_el.get_text()) if price_el else fallback_price

    # Detect currency
    raw_price = price_el.get_text().strip() if price_el else ""
    currency = fallback_currency
    if "$" in raw_price:
        currency = "USD"
    elif "₹" in raw_price:
        currency = "INR"
    elif "£" in raw_price:
        currency = "GBP"

    return {
        "product_name": product_name,
        "current_price": price,
        "currency": currency,
        "url": url,
        "source": "amazon",
        "timestamp": _now_iso()
    }

if __name__ == "__main__":
    # List of product URLs

    PRODUCT_URLS = [
    "https://www.amazon.com/dp/B0FFTS7G7R",  # Pixel 10
    "https://www.amazon.com/dp/B0F7K9LFCL",  # Samsung fold
    "https://www.amazon.com/dp/B0DLHLRDBY",  # Samsung A16
    ]


    results = []
    for url in PRODUCT_URLS:
        data = scrape_product(url, fallback_name="Amazon Product", fallback_price=999.99)
        results.append(data)

    # Save to JSON
    pathlib.Path("data").mkdir(exist_ok=True)
    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    out_path = f"data/raw_prices_{date_str}.json"

    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Scraping complete. Saved data → {out_path}")
    for item in results:
        print(item)
