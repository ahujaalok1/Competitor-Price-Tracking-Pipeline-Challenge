# Author: Alok Ahuja - Lead Data Engineer

# Competitor Price Tracking Pipeline

A simple ETL pipeline to monitor daily competitor prices from Amazon.
Built with Python, Apache Airflow, and Streamlit.

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


## Project Structure
- `scraper.py` → Extracts product prices (raw JSON).
- `etl.py` → Transforms data, calculates price changes (cleaned JSON).
- `dags/price_tracker.py` → Airflow DAG for daily automation.
- `dashboard.py` → dashboard to view results.
- `data/` → Stores raw and cleaned output JSONs (ignored in repo).

## How It Works
1. **Extraction** → Scrapes Amazon prices for selected products.
2. **Transformation** → Cleans data, calculates daily price changes.
3. **Loading** → Saves structured JSON.
4. **Orchestration** → Airflow automates daily runs.
5. **Visualization** → dashboard shows price history.

# Run manually
python scraper.py
python etl.py
dashboard.py
