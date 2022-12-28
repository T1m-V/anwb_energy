from datetime import date, datetime, timedelta

import dash
import dash_bootstrap_components as dbc
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

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(
        {"Time": pd.date_range(start=selected_date, freq="H", periods=24), "Price (€)": prices}
    )
    df["Time"] = pd.to_datetime(df["Time"], unit="h")
    df.set_index("Time", inplace=True)

    # Plot the data using plotly
    # This weird try except loop fixes the invalid value error upon first starting.
    try:
        fig_hourly = px.line(df, x=df.index, y="Price (€)")
    except Exception as e:
        if str(e) != "Invalid value":
            print(e)
        fig_hourly = px.line(df, x=df.index, y="Price (€)")
    return fig_hourly


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
        df = pd.DataFrame(
            {"Time": pd.date_range(start=start, freq="H", periods=24 * 7), "Price (€)": prices}
        )

    df["Time"] = pd.to_datetime(df["Time"], unit="h")
    df.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig = px.line(df, x=df.index, y="Price (€)")

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
        df = pd.DataFrame(
            {"Time": pd.date_range(start=start, freq="H", periods=24 * 30), "Price (€)": prices}
        )

    df["Time"] = pd.to_datetime(df["Time"], unit="h")
    df.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig = px.line(df, x=df.index, y="Price (€)")

    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
