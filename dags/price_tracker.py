"""
price_tracker.py
----------------
Airflow DAG to orchestrate the competitor price tracking pipeline.

Workflow:
1. Run scraper.py → Extract raw prices for iPhone 14 (DE1).
2. Run etl.py → Transform & Load cleaned data with price changes (DE2).
3. Save final data for visualization.

Schedule: Daily
Start Date: 29-Aug-2025

Author: Alok Ahuja - Data Engineer
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments for DAG tasks
default_args = {
    "owner": "data_team",
    "depends_on_past": False,         # Each run is independent
    "retries": 1,                     # Retry once if task fails
    "retry_delay": timedelta(minutes=5)  # Wait 5 mins before retry
}

# Define the DAG
with DAG(
    "price_tracker",                          # DAG name
    default_args=default_args,
    description="Daily competitor price tracker for iPhone 14",
    schedule_interval="@daily",               # Run once daily
    start_date=datetime(2025, 8, 29),         # First execution date
    catchup=False,                            # Do not backfill old runs
    tags=["etl", "scraping", "amazon"],       # Useful for categorization in Airflow UI
) as dag:

    # Task 1: Run scraper.py (Extraction)
    scrape_task = BashOperator(
        task_id="scrape_prices",
        bash_command="python /opt/airflow/scraper.py"
    )

    # Task 2: Run etl.py (Transformation + Load)
    etl_task = BashOperator(
        task_id="transform_load",
        bash_command="python /opt/airflow/etl.py"
    )

    # Define task dependency (scrape → etl)
    scrape_task >> etl_task

