# Competitor Price Tracking Pipeline

An automated pipeline to **scrape, clean, and track competitor product prices** with visualization through a dashboard.  
Built with **Python, Apache Airflow, and Dash**.

---

## Features
- **Web Scraping** – Collects product prices from e-commerce websites (Amazon demo).
- **ETL Pipeline** – Extracts raw prices, transforms product details, and saves cleaned data.
- **Price Tracking** – Computes daily changes (`price_change` and `price_change_pct`) across products.
- **Dashboard** – Interactive web dashboard to visualize product prices and trends.
- **Scheduling** – Automated daily execution using **Airflow DAG**.

---

## Project Structure
```
Competitor-Price-Tracking-Pipeline-Challenge/
│── competitor_price_tracking/
│   ├── scraper.py        # Scrapes raw product prices
│   ├── etl.py            # Cleans and transforms raw data
│── dags/
│   └── price_tracker.py  # Airflow DAG definition
│── data/
│   ├── raw_prices/       # Raw JSON files from scraping
│   ├── cleaned_prices/   # Cleaned JSON files after ETL
│── dashboard.py          # Dash-based visualization
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation
│── .gitignore            # Ignored files for Git
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/Competitor-Price-Tracking-Pipeline-Challenge.git
cd Competitor-Price-Tracking-Pipeline-Challenge
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

### Run Airflow DAG
Clone the repository and set up the environment:

```bash
git clone <repo_url>
cd Competitor-Price-Tracking-Pipeline-Challenge
pip install -r requirements.txt
```

Initialize Airflow and start services:

```bash
airflow db init
airflow webserver
airflow scheduler
```

### Run Dashboard
```bash
python dashboard.py
```
- Access dashboard at: [http://127.0.0.1:8050](http://127.0.0.1:8050)  
- View daily prices, changes, and trends.

---

## Example Output
- **Scraped Raw Data:** `data/raw_prices/raw_prices_2025-09-07.json`
- **Cleaned Data:** `data/cleaned_prices/cleaned_prices_2025-09-07.json`
- **Dashboard:** Interactive charts of product price trends.

---

## Tech Stack
- **Python** – Core scripting
- **BeautifulSoup** – Web scraping
- **Pandas** – Data cleaning & transformation
- **Apache Airflow** – Workflow orchestration
- **Dash / Plotly** – Interactive dashboard
- **JSON** – Storage format for daily data

---

## Data Example

### Raw Data (`data/raw_prices/`)
```json
[
  {
    "product_name": "Google Pixel 10 Pro ...",
    "current_price": 1049.0,
    "currency": "USD",
    "url": "https://www.amazon.com/dp/B0FFTS7G7R",
    "source": "amazon",
    "timestamp": "2025-09-07T19:07:08+05:30"
  }
]
```

### Cleaned Data (`data/cleaned_prices/`)
```json
[
  {
    "product_name": "Pixel 10 Pro",
    "current_price": 1049.0,
    "currency": "USD",
    "price_change": 50.0,
    "price_change_pct": 5.0,
    "timestamp": "2025-09-07T19:07:08+05:30"
  }
]
```

## Future Improvements
- Add more e-commerce sources (Flipkart, Walmart, etc.)
- Automate dashboard refresh via Airflow.
- Store data in a database (PostgreSQL/BigQuery) instead of JSON.
- Add alerts for significant price drops.

---

## Author
**Alok Ahuja**  
Data Engineer | Software Developer | Big Data & Cloud Enthusiast  

---
