# Author: Alok Ahuja – Lead Data Engineer  

# Competitor Price Tracking Pipeline  

A simple ETL pipeline to monitor daily competitor prices from Amazon.  
Built with **Python, Apache Airflow, and Dash/Plotly**.  

---

## Project Overview  
The pipeline performs three key steps:  

1. **Scraper (`scraper.py`)**  
   - Extracts raw product price data from Amazon search results.  
   - Saves as `raw_data_YYYY-MM-DD.json`.  

2. **ETL (`etl.py`)**  
   - Reads raw JSON files from the scraper.  
   - Cleans data (converts price to float, removes missing values).  
   - Compares with previous day's data to calculate **price changes**.  
   - Saves structured output as `data/prices_YYYY-MM-DD.json`.  

3. **Dashboard (`dashboard.py`)**  
   - Built with **Dash + Plotly**.  
   - Loads cleaned JSON files from the ETL step.  
   - Provides:  
     - **Overview table** → Today’s snapshot of prices.  
     - **Historical trends** → Line charts for all products across multiple days.  
     - **Explorer tab** → Interactive dropdown to view price & % change for a product.  

---

## Project Structure  
- `scraper.py` → Extracts product prices (raw JSON).  
- `etl.py` → Transforms data, calculates price changes (cleaned JSON).  
- `dags/price_tracker.py` → Airflow DAG for daily automation.  
- `dashboard.py` → Dashboard to view results.  
- `data/` → Stores raw and cleaned output JSONs.  

---

## How It Works  
1. **Extraction** → Scrapes Amazon prices for selected products.  
2. **Transformation** → Cleans data, calculates daily price changes.  
3. **Loading** → Saves structured JSON.  
4. **Orchestration** → Airflow automates daily runs.  
5. **Visualization** → Dashboard shows price history.  

---

## Setup Instructions  

### 1. Clone the Repository  
```bash
git clone https://github.com/<your-username>/competitor-price-tracker.git
cd competitor-price-tracker
```  

### 2. Create a Virtual Environment  
```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```  

### 3. Install Dependencies  
```bash
pip install -r requirements.txt
```  

If `requirements.txt` is missing:  
```bash
pip install requests beautifulsoup4 pandas dash plotly apache-airflow
```  

### 4. Start Airflow (for orchestration)  
```bash
airflow db init
airflow users create \\
    --username admin \\
    --password admin \\
    --firstname Data \\
    --lastname Engineer \\
    --role Admin \\
    --email admin@example.com
```

**Start scheduler and webserver:**  
```bash
airflow scheduler &
airflow webserver -p 8080
```

Airflow UI → `http://127.0.0.1:8080`  

---

## How to Run the Pipeline and Dashboard  

### Step 1: Run Scraper  
```bash
python scraper.py
```
Creates `raw_data_YYYY-MM-DD.json` in `/data`.  

### Step 2: Run ETL  
```bash
python etl.py
```
Creates `prices_YYYY-MM-DD.json` in `/data`.  

### Step 3: Orchestrate with Airflow  
- DAG file: `dags/price_tracker.py`  
- Airflow UI → Trigger DAG manually or let it run on schedule.  
- Tasks:  
  - `scrape_task` → runs scraper  
  - `transform_task` → cleans + enriches data  
  - `load_task` → saves to structured JSON  

### Step 4: Launch Dashboard  
```bash
python dashboard.py
```
Opens at → `http://127.0.0.1:8050`  

---

## Expected Outputs  

**Raw Data (`raw_data_YYYY-MM-DD.json`)**  
```json
[
  {
    "product_name": "iPhone 14",
    "price": 799.99,
    "url": "https://amazon.com/...",
    "timestamp": "2025-08-29"
  }
]
```

**ETL Output (`prices_YYYY-MM-DD.json`)**  
```json
[
  {
    "product_name": "iPhone 14",
    "current_price": 799.99,
    "price_change": -10.0,
    "price_change_pct": -1.24,
    "timestamp": "2025-08-29"
  }
]
```

**Dashboard**  
- **Table**: Today’s prices  
- **Line Chart**: Historical prices per product  
- **Bar Chart**: Daily % changes  

---

## Assumptions  

- **Scraping Reliability**  
  - Amazon may block or throttle scraping due to bot detection.  
  - Implemented **User-Agent rotation** and `Accept-Language` headers.  
  - Added **5–10 second delays (recommended)** to avoid blocks.  

- **Fallback Mechanism**  
  - If scraping fails (blocked, HTML changed, missing elements), the script automatically falls back to **mock values**.  
  - Mock values are **predefined per ASIN** in the `FALLBACKS` dictionary of `scraper.py`.  
  - Fallbacks include product name, price, and currency (e.g., Pixel 10 → $899.99).  

- **Data Storage**  
  - Each run saves data into `data/raw_prices_YYYY-MM-DD.json`.  
  - Data is stored in **JSON** for portability; future extension can include SQLite/Postgres.  

- **Products Tracked**  
  - Currently limited to **3 products (Pixel 10, Samsung Fold, Samsung A16)**.  
  - Can be expanded by updating the `PRODUCT_URLS` list in `scraper.py`.  

- **ETL Dependencies**  
  - ETL (`etl.py`) expects at least one valid JSON file from the scraper.  
  - If no previous file exists → **price change defaults to 0**.  

- **Airflow**  
  - Local demo uses cron (`0 0 * * *`).  
  - Production: use managed Airflow (AWS MWAA / GCP Composer).  

---

## Future Enhancements  
- Deploy with **Docker + Docker Compose**  
- Store data in **SQLite/Postgres** instead of JSON  
- Add **CI/CD workflows** for pipeline updates  
- Enable **CSV/JSON export** from dashboard  
