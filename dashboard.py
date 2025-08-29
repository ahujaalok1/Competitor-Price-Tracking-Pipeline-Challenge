"""
dashboard.py
------------
Simple Streamlit dashboard for competitor price tracking.

- Reads cleaned JSON data from ETL pipeline.
- Displays table of current prices with price change.
- Plots historical price trend for each product.

Author: Alok Ahuja - Data Engineer
"""

import json
import pathlib
import pandas as pd
from datetime import datetime

import dash
from dash import dcc, html, dash_table
import plotly.express as px

# ------------------------
# Data loading
# ------------------------
DATA_DIR = pathlib.Path("data")

def load_latest():
    files = sorted(DATA_DIR.glob("prices_*.json"))
    if not files:
        return None
    latest = files[-1]
    with open(latest, "r") as f:
        return json.load(f)

def load_all():
    all_files = sorted(DATA_DIR.glob("prices_*.json"))
    records = []
    for f in all_files:
        with open(f, "r") as fh:
            records.extend(json.load(fh))
    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df, len(all_files)

latest_data = load_latest()
df_all, num_days = load_all()

# ------------------------
# Dash App Layout
# ------------------------
app = dash.Dash(__name__)
app.title = "Competitor Price Tracker"

app.layout = html.Div([
    html.H1("Competitor Price Tracker"),
    html.P("Monitoring daily competitor prices for key products."),

    # Latest snapshot
    html.H2("Today's Snapshot"),
    dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in pd.DataFrame(latest_data).columns],
        data=pd.DataFrame(latest_data).to_dict("records"),
        style_table={"overflowX": "auto"},
        page_size=10,
    ),

    html.Br(),

    # Historical overview
    html.H2(f"Historical Trends (showing {num_days} days)"),
    dcc.Graph(
        id="all-products-chart",
        figure=px.line(
            df_all,
            x="timestamp",
            y="current_price",
            color="product_name",
            title="Price Trends for All Products",
            markers=True
        )
    ),

    html.Br(),

    # Product explorer
    html.H2("🔎 Explore a Product"),
    dcc.Dropdown(
        id="product-dropdown",
        options=[{"label": p, "value": p} for p in df_all["product_name"].unique()],
        value=df_all["product_name"].unique()[0],
        clearable=False,
        style={"width": "300px"}
    ),
    dcc.Graph(id="product-price-chart"),
    dcc.Graph(id="product-pct-chart"),
])

# ------------------------
# Callbacks for interactivity
# ------------------------
@app.callback(
    [dash.dependencies.Output("product-price-chart", "figure"),
     dash.dependencies.Output("product-pct-chart", "figure")],
    [dash.dependencies.Input("product-dropdown", "value")]
)
def update_product_charts(selected_product):
    subset = df_all[df_all["product_name"] == selected_product].sort_values("timestamp")

    # Price trend
    price_fig = px.line(
        subset,
        x="timestamp",
        y="current_price",
        title=f"{selected_product} Price Trend",
        markers=True
    )

    # % Change trend
    pct_fig = px.bar(
        subset,
        x="timestamp",
        y="price_change_pct",
        title=f"{selected_product} Daily % Change"
    )

    return price_fig, pct_fig

# ------------------------
# Run the app
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)