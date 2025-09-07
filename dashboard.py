"""
Dashboard: Competitor Price Tracker
-----------------------------------
Dash app to visualize competitor prices.

Features:
- Shows latest scraped prices.
- Historical price trends across products.
- Interactive product explorer with % change visualization.

Author: Alok Ahuja
"""

import json
import pathlib
import pandas as pd
from datetime import datetime

import dash
from dash import dcc, html, dash_table
import plotly.express as px

# Data directory
PROJECT_ROOT = pathlib.Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data" / "cleaned_prices"

def load_latest():
    """Load the most recent JSON file with prices."""
    files = sorted(DATA_DIR.glob("prices_*.json"))
    if not files:
        raise FileNotFoundError(f"No price JSON files found in {DATA_DIR}")
    latest = files[-1]
    with open(latest, "r") as f:
        data = json.load(f)
        if not data:
            raise ValueError(f"The latest file {latest} is empty")
        return data

def load_all():
    """Load and combine all historical price files into a DataFrame."""
    all_files = sorted(DATA_DIR.glob("prices_*.json"))
    if not all_files:
        raise FileNotFoundError(f"No price JSON files found in {DATA_DIR}")
    records = []
    for f in all_files:
        with open(f, "r") as fh:
            records.extend(json.load(fh))
    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df, len(all_files)

# Load data
latest_data = load_latest()
df_all, num_days = load_all()

# Preprocess data

def shorten_product_name(full_name: str) -> str:
    """Map full product names to short, clean names. """
    full_name_lower = full_name.lower()

    if "pixel 10 pro" in full_name_lower:
        return "Pixel 10 Pro"
    elif "Samsung Galaxy Z Fold7" in full_name_lower:
        return "Samsung Galaxy Z Fold7"
    elif "samsung galaxy a16" in full_name_lower:
        return "Samsung Galaxy A16"
    else:
        return " ".join(full_name.split()[:3]).title()

for item in latest_data:
    if "product_name" in item:
        item["product_name"] = shorten_product_name(item["product_name"])
    if "url" in item:
        del item["url"]

# Shorten names in historical df
df_all["product_name"] = df_all["product_name"].apply(shorten_product_name)
if "url" in df_all.columns:
    df_all = df_all.drop(columns=["url"])


# Dash App Layout
app = dash.Dash(__name__)
app.title = "Competitor Price Tracker"

app.layout = html.Div([
    html.H1("Competitor Price Tracker"),
    html.P("Daily monitoring of competitor prices for key products."),

    # Today's snapshot
    html.H2("Today's Snapshot"),
    dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in pd.DataFrame(latest_data).columns],
        data=pd.DataFrame(latest_data).to_dict("records"),
        style_table={"overflowX": "auto"},
        page_size=10,
    ),

    html.Hr(),

    # Historical trends
    html.H2(f"Historical Trends (last {num_days} days)"),
    dcc.Graph(
        id="all-products-chart",
        figure=px.line(
            df_all,
            x="timestamp",
            y="current_price",
            color="product_name",
            title="Price Trends for All Products",
            markers=True,
        ),
    ),

    html.Hr(),

    # Product Explorer
    html.H2("Explore a Product"),
    dcc.Dropdown(
        id="product-dropdown",
        options=[{"label": p, "value": p} for p in df_all["product_name"].unique()],
        value=df_all["product_name"].unique()[0],
        clearable=False,
        style={"width": "300px"},
    ),
    dcc.Graph(id="product-price-chart"),
    dcc.Graph(id="product-pct-chart"),
])

# Callbacks
@app.callback(
    [dash.dependencies.Output("product-price-chart", "figure"),
     dash.dependencies.Output("product-pct-chart", "figure")],
    [dash.dependencies.Input("product-dropdown", "value")]
)
def update_product_charts(selected_product):
    """Update charts when a product is selected."""
    subset = df_all[df_all["product_name"] == selected_product].sort_values("timestamp")

    # Price trend
    price_fig = px.line(
        subset,
        x="timestamp",
        y="current_price",
        title=f"{selected_product} Price Trend",
        markers=True,
    )

    # % Change trend
    pct_fig = px.bar(
        subset,
        x="timestamp",
        y="price_change_pct",
        title=f"{selected_product} Daily % Change",
    )

    return price_fig, pct_fig

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)