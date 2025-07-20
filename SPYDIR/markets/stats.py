import numpy as np
from scipy import interpolate
import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET


def get_erp() -> float:
    """Returns Equity Risk Premium

    TODO - add calculation
    """
    return 4.33 / 100


def get_forex_rates() -> dict:
    """Fetch global exchange rates and return a dictionary

    Returns:
        dict: Keys: USD_* and GBP_* for common exchange rates
    """

    res = requests.get(
        f"https://cdn.jsdelivr.net/gh/prebid/currency-file@1/latest.json?date={datetime.today().strftime('%Y%m%d')}"
    )
    data = json.loads(res.text)["conversions"]

    currency = {}

    for base, prices in data.items():
        for price, value in prices.items():
            if price != base:
                currency[f"{base}_{price}"] = value

    return currency


def get_interest_rate(t: float) -> float:
    """
    Interpolate risk free rate for any time t.
    Uses cubic spline as used in vix method.

    Args:
        t (float): Time in years

    Returns:
        float: Rate for 0 -> t
    """
    x = np.array(
        [1 / 12, 1.5 / 12, 2 / 12, 3 / 12, 4 / 12, 6 / 12, 1, 2, 3, 5, 7, 10, 20, 30]
    )

    api_url = "https://home.treasury.gov/sites/default/files/interest-rates/yield.xml"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = requests.get(api_url, headers=headers)

    xml_str = res.content.decode("utf-8")
    xml_data = ET.fromstring(xml_str)

    # All Days
    days = xml_data.findall(
        ".//LIST_G_WEEK_OF_MONTH//G_WEEK_OF_MONTH//LIST_G_NEW_DATE//G_NEW_DATE"
    )
    # Most recent
    cur = days[-1]
    # Find list of dates
    times = cur.find(".//LIST_G_BC_CAT//G_BC_CAT")
    rates = []

    for child in times[0 : len(x)]:
        rates.append(float(child.text) / 100)

    r_func = interpolate.CubicSpline(x, rates)

    return float(r_func(np.array(t)))


# TODO - add inflation
# def get_inflation_rates():

#     return
