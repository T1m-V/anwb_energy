from datetime import date, datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

from load_data import create_historic_overview, get_price_curve, get_raw_energy_prices

# Calculate the start date as two weeks back from today
start_date = date.today() - timedelta(weeks=2)

today = date.today()
# Calculate the end date as tomorrow
end_date = date.today() + timedelta(days=1)

# Initialize the app
external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    {
        "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "rel": "stylesheet",
        "integrity": "sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO",
        "crossorigin": "anonymous",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


navigation = dbc.Card(
    dbc.CardBody(
        [
            html.H1("Select your product."),
            dcc.RadioItems(
                id="product-source",
                options=[{"label": "Power", "value": "power"}, {"label": "Gas", "value": "gas"}],
                value="power",
            ),
            html.H1("Select your date."),
            dcc.DatePickerSingle(
                id="date-picker",
                min_date_allowed=start_date,
                max_date_allowed=end_date,
                initial_visible_month=today,
                date=today,
            ),
        ],
    ),
    className="mt-2 ml-2",
)

hourly_card = (
    dbc.Card(
        children=dbc.CardBody(
            dcc.Graph(
                id="hourly-prices",
                style={
                    "width": "100%",
                    "height": "100%",
                    "display": "inline-block",
                },
            ),
        ),
    ),
)

weekly_card = (
    dbc.Card(
        [
            dbc.CardBody(
                dcc.Graph(
                    id="weekly-prices",
                    style={
                        "width": "100%",
                        "height": "100%",
                        "display": "inline-block",
                    },
                )
            ),
        ],
    ),
)

monthly_card = (
    dbc.Card(
        [
            dbc.CardBody(
                dcc.Graph(
                    id="monthly-prices",
                    style={
                        "width": "100%",
                        "height": "100%",
                        "display": "inline-block",
                    },
                )
            ),
        ],
    ),
)

# Define the layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [navigation],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Tabs(
                            [
                                dcc.Tab(
                                    label="Hourly Prices",
                                    children=hourly_card,
                                ),
                                dcc.Tab(
                                    label="Weekly Prices",
                                    children=weekly_card,
                                ),
                                dcc.Tab(
                                    label="Monthly Prices",
                                    children=monthly_card,
                                ),
                            ],
                        ),
                    ],
                    width=9,
                ),
            ],
        ),
    ],
    style={"height": "100vh"},
    fluid=True,
)


# Define the callback function to update the graph
@app.callback(
    Output("hourly-prices", "figure"),
    Input("date-picker", "date"),
    Input("product-source", "value"),
)
def update_hourly_figure(selected_date, sort):
    # Retrieve the data for the selected date using the get_price_curve function
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    data = get_raw_energy_prices(selected_date, sort)
    prices = get_price_curve(data)

    # If power than also add daily average
    if sort == "gas":
        df = pd.DataFrame(
            {
                "Time": pd.date_range(start=selected_date, freq="H", periods=24),
                "Price (€)": prices,
            }
        )
    else:

        ma = [np.mean(prices)] * len(prices)

        # Convert the data to a Pandas DataFrame
        df = pd.DataFrame(
            {
                "Time": pd.date_range(start=selected_date, freq="H", periods=24),
                "Price (€)": prices,
                "Daily Average (€)": ma,
            }
        )

    df["Time"] = pd.to_datetime(df["Time"], unit="h")
    df.set_index("Time", inplace=True)

    # Plot the data using plotly
    # This weird try except loop fixes the invalid value error upon first starting.
    try:
        fig = px.line(df, x=df.index, y=df.columns[0:])
    except Exception as e:
        if str(e) != "Invalid value":
            print(e)
        fig = px.line(df, x=df.index, y=df.columns[0:])

    fig.update_layout(
        title="Daily Overview",
        xaxis_title="Day",
        yaxis_title="Price (€)",
        legend_title="",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    return fig


@app.callback(
    Output("weekly-prices", "figure"),
    Input("date-picker", "date"),
    Input("product-source", "value"),
)
def update_weekly_figure(selected_date, sort):
    # Retrieve the data for the selected date using the get_price_curve function
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    prices = create_historic_overview(selected_date, 7, sort)

    # Convert the data to a Pandas DataFrame
    start = selected_date - timedelta(days=7)
    if sort == "gas":
        df = pd.DataFrame(
            {"Time": pd.date_range(start=start, freq="D", periods=7), "Price (€)": prices}
        )
    else:
        day_before = selected_date - timedelta(7)
        price_day_before = get_price_curve(get_raw_energy_prices(day_before, sort))

        # Calculate daily average
        ma = [0] * len(prices)
        for i in range(len(prices)):
            range_min = i - 24

            if range_min < 0:
                ma_el = (sum(price_day_before[range_min:]) + sum(prices[:i])) / 24
            else:
                ma_el = sum(prices[range_min:i]) / 24
            ma[i] = ma_el

        df = pd.DataFrame(
            {
                "Time": pd.date_range(start=start, freq="H", periods=24 * 7),
                "Price": prices,
                "Daily Average": ma,
            }
        )

    df["Time"] = pd.to_datetime(df["Time"], unit="h")
    df.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig = px.line(df, x=df.index, y=df.columns[0:])
    fig.update_layout(
        title="Weekly Overview",
        xaxis_title="Day",
        yaxis_title="Price (€)",
        legend_title="",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    return fig


@app.callback(
    Output("monthly-prices", "figure"),
    Input("date-picker", "date"),
    Input("product-source", "value"),
)
def update_monthly_figure(selected_date, sort):
    # Retrieve the data for the selected date using the get_price_curve function
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    prices = create_historic_overview(selected_date, 30, sort)

    # Convert the data to a Pandas DataFrame
    start = selected_date - timedelta(days=30)
    if sort == "gas":
        df = pd.DataFrame(
            {"Time": pd.date_range(start=start, freq="D", periods=30), "Price (€)": prices}
        )
    else:
        day_before = selected_date - timedelta(30)
        price_day_before = get_price_curve(get_raw_energy_prices(day_before, sort))

        # Calculate daily average
        ma = [0] * len(prices)
        for i in range(len(prices)):
            range_min = i - 24

            if range_min < 0:
                ma_el = (sum(price_day_before[range_min:]) + sum(prices[:i])) / 24
            else:
                ma_el = sum(prices[range_min:i]) / 24
            ma[i] = ma_el

        df = pd.DataFrame(
            {
                "Time": pd.date_range(start=start, freq="H", periods=24 * 30),
                "Hourly Price": prices,
                "Daily Average": ma,
            }
        )

    df["Time"] = pd.to_datetime(df["Time"], unit="h")
    df.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig = px.line(df, x=df.index, y=df.columns[0:])

    fig.update_layout(
        title="Monthly Overview",
        xaxis_title="Day",
        yaxis_title="Price (€)",
        legend_title="",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
