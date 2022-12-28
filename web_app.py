from datetime import date, datetime, timedelta

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

from load_data import get_price_curve, get_raw_energy_prices

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


# Define the layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                [
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
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Tabs(
                            id="tab",
                            children=[
                                dcc.Tab(
                                    label="Electricity Prices",
                                    children=[
                                        dbc.Card(
                                            children=dbc.CardBody(
                                                dcc.Graph(
                                                    id="hourly-prices-electricity",
                                                    style={
                                                        "width": "100%",
                                                        "height": "100%",
                                                        "display": "inline-block",
                                                    },
                                                ),
                                            ),
                                        ),
                                    ],
                                ),
                                dcc.Tab(
                                    label="Gas Prices",
                                    children=[
                                        dbc.Card(
                                            [
                                                dbc.CardBody(
                                                    dcc.Graph(
                                                        id="hourly-prices-gas",
                                                        style={
                                                            "width": "100%",
                                                            "height": "100%",
                                                            "display": "inline-block",
                                                        },
                                                    )
                                                ),
                                            ],
                                        ),
                                    ],
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
    Output("hourly-prices-gas", "figure"),
    Output("hourly-prices-electricity", "figure"),
    Input("date-picker", "date"),
)
def update_figure(selected_date):
    # Retrieve the data for the selected date using the get_price_curve function
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    gas_data = get_raw_energy_prices(selected_date, "gas")
    gas_prices = get_price_curve(gas_data)

    # Convert the data to a Pandas DataFrame
    df_gas = pd.DataFrame(
        {"Time": pd.date_range(start=selected_date, freq="H", periods=24), "Price (€)": gas_prices}
    )
    df_gas["Time"] = pd.to_datetime(df_gas["Time"], unit="h")
    df_gas.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig_gas = px.line(df_gas, x=df_gas.index, y="Price (€)")

    electricity_data = get_raw_energy_prices(selected_date, "electricity")
    electricity_prices = get_price_curve(electricity_data)

    # Convert the data to a Pandas DataFrame
    df_electricity = pd.DataFrame(
        {
            "Time": pd.date_range(start=selected_date, freq="H", periods=24),
            "Price (€)": electricity_prices,
        }
    )
    df_electricity["Time"] = pd.to_datetime(df_electricity["Time"], unit="h")
    df_electricity.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig_electricity = px.line(df_electricity, x=df_electricity.index, y="Price (€)")
    return fig_gas, fig_electricity


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
