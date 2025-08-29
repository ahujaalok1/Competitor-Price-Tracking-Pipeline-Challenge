# Author: Alok Ahuja - Lead Data Engineer

# Competitor Price Tracking Pipeline

A simple ETL pipeline to monitor daily competitor prices from Amazon.
Built with Python, Apache Airflow, and Streamlit.

## Project Structure
- `scraper.py` → Extracts product prices (raw JSON).
- `etl.py` → Transforms data, calculates price changes (cleaned JSON).
- `dags/price_tracker.py` → Airflow DAG for daily automation.
- `dashboard.py` → Streamlit dashboard to view results.
- `data/` → Stores raw and cleaned output JSONs (ignored in repo).

## How It Works
1. **Extraction** → Scrapes Amazon prices for selected products.
2. **Transformation** → Cleans data, calculates daily price changes.
3. **Loading** → Saves structured JSON.
4. **Orchestration** → Airflow automates daily runs.
5. **Visualization** → Streamlit dashboard shows price history.

# Run manually
python scraper.py
python etl.py
streamlit run dashboard.py
