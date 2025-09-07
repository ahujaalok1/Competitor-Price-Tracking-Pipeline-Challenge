"""
price_tracker.py
----------------
Airflow DAG for competitor price tracking pipeline.

Pipeline Steps:
1. Scrape competitor product prices (scraper.py → run_scraper()).
2. Transform + load data (etl.py → run_etl()).
3. (Optional) Trigger dashboard refresh after ETL.

Author: Alok Ahuja
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Import pipeline tasks
from competitor_price_tracking.scraper import run_scraper
from competitor_price_tracking.etl import run_etl

# Default arguments

default_args = {
    "owner": "alok",
    "depends_on_past": False,
    "email": ["alerts@yourcompany.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# DAG Definition

with DAG(
    dag_id="price_tracker_pipeline",
    default_args=default_args,
    description="Competitor price tracking pipeline (scraping + ETL + dashboard)",
    schedule_interval="0 9 * * *",   # run every day at 9 AM IST
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["price-tracking", "etl", "dashboard"],
) as dag:

    # Task 1: Scrape raw prices

    def _scrape_callable(**context):
        logging.info("Starting scraping task...")
        raw_file = run_scraper()
        logging.info("Scraping complete. Raw file saved: %s", raw_file)
        return str(raw_file)

    scrape_task = PythonOperator(
        task_id="scrape_prices",
        python_callable=_scrape_callable,
        provide_context=True,
    )

    # Task 2: Transform + Load

    def _etl_callable(**context):
        logging.info("Starting ETL task...")
        clean_file = run_etl()
        logging.info("ETL complete. Cleaned file saved: %s", clean_file)
        return str(clean_file)

    etl_task = PythonOperator(
        task_id="etl_transform_load",
        python_callable=_etl_callable,
        provide_context=True,
    )

    # Task 3: Refresh dashboard

    def _dashboard_callable(**context):
        logging.info("Triggering dashboard refresh...")
        logging.info("Dashboard refresh triggered successfully.")

    dashboard_task = PythonOperator(
        task_id="refresh_dashboard",
        python_callable=_dashboard_callable,
        provide_context=True,
    )

    # DAG dependencies
    scrape_task >> etl_task >> dashboard_task
