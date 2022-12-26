import json
import os
import urllib.request
from datetime import date, timedelta

import numpy as np


def energyzero_api_loader_today_tomorrow(today, usage):
    urlbase = "https://api.energyzero.nl/v1/energyprices?"

    # Define date range
    yesterday = today - timedelta(days=1)
    fromDate = str(yesterday) + "T23%3A00%3A00.000Z"
    tillDate = str(today) + "T22%3A00%3A00.000Z"

    # Constants
    interval = 4
    inclBtw = "True"

    # Construct URL
    url = (
        urlbase
        + "fromDate="
        + fromDate
        + "&tillDate="
        + tillDate
        + "&interval="
        + str(interval)
        + "&usageType="
        + str(usage)
        + "&inclBtw="
        + inclBtw
    )

    # Get data from URL
    with urllib.request.urlopen(url) as urlopener:
        data = json.load(urlopener)

    return data


def get_raw_energy_prices(today, sort):
    # Define paths
    libPath = f"./backlog_{sort}/{str(today)}{sort}.npy"

    # Check if we already have the data otherwise load it from API
    if os.path.exists(libPath):
        data = np.load(libPath, allow_pickle=True).item()
    else:
        if sort == "gas":
            usage = 3
        elif sort == "electricity":
            usage = 1
        else:
            print("Do not know how to handle the energy prices of sort:", sort)
            return None
        data = energyzero_api_loader_today_tomorrow(today, usage)

    # Check if the data already exists, otherwise return None and try later again.
    if len(data["Prices"]) != 24:
        return None

    # Save data for later use
    np.save(libPath, data)

    return data


def get_price_curve(data):
    # If not available, display 0.
    if not data:
        return [0] * 24

    # Collect data and add to hourly curve.
    todayPrices = data["Prices"]
    curve = []
    for i in range(len(todayPrices)):
        curve.append(todayPrices[i]["price"])
    return curve


if __name__ == "__main__":
    # Specify the day we want the energy prices.
    today = date.today()
    wantedDay = today - timedelta(days=4)

    # Collect the data
    dataGas = get_raw_energy_prices(wantedDay, "gas")
    dataElectricity = get_raw_energy_prices(wantedDay, "electricity")

    gasCurve = get_price_curve(dataGas)
    electricityCurve = get_price_curve(dataElectricity)

    # Print the data
    print("The electricity prices for", wantedDay, "are: ", electricityCurve)
    print("The gas prices for", wantedDay, "are: ", gasCurve)
