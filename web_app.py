from datetime import date, datetime, timedelta

import dash
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
app = dash.Dash()

# Define the layout of the app
app.layout = html.Div(
    [
        dcc.Graph(
            id="hourly-prices-electricity",
            style={"height": "300px", "width": "100%", "display": "inline-block"},
        ),
        dcc.Graph(
            id="hourly-prices-gas",
            style={"height": "300px", "width": "100%", "display": "inline-block"},
        ),
        dcc.DatePickerSingle(
            id="date-picker",
            min_date_allowed=start_date,
            max_date_allowed=end_date,
            initial_visible_month=today,
            date=today,
        ),
    ]
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
    gasData = get_raw_energy_prices(selected_date, "gas")
    gasPrices = get_price_curve(gasData)

    # Convert the data to a Pandas DataFrame
    df_gas = pd.DataFrame(
        {"Time": pd.date_range(start=selected_date, freq="H", periods=24), "Price (€)": gasPrices}
    )
    df_gas["Time"] = pd.to_datetime(df_gas["Time"], unit="h")
    df_gas.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig_gas = px.line(df_gas, x=df_gas.index, y="Price (€)")

    electricityData = get_raw_energy_prices(selected_date, "electricity")
    electricityPrices = get_price_curve(electricityData)

    # Convert the data to a Pandas DataFrame
    df_electricity = pd.DataFrame(
        {
            "Time": pd.date_range(start=selected_date, freq="H", periods=24),
            "Price (€)": electricityPrices,
        }
    )
    df_electricity["Time"] = pd.to_datetime(df_electricity["Time"], unit="h")
    df_electricity.set_index("Time", inplace=True)

    # Plot the data using plotly
    fig_electricity = px.line(df_electricity, x=df_electricity.index, y="Price (€)")
    return fig_gas, fig_electricity


# Run the app
if __name__ == "__main__":
    app.run_server()
