# For plotly history
import pandas as pd
from datetime import datetime
from yahooquery import Ticker
from .utils.format_helpers import *


def get_history(ticker):

    methods = {"YQ": fetch_history_yq}

    for key, method in methods.items():
        try:
            history = method(str(ticker))
            if history:
                return history
        except RuntimeError as e:  # If API fails, continue to next
            continue
    return None


def fetch_history_yq(ticker):

    yq_tick = Ticker(ticker)
    yq_hist = yq_tick.history(period="1y")

    time_dict = yq_hist.reset_index()[["date", "open", "high", "low", "close"]]

    time_dict["date"] = time_dict["date"].apply(
        lambda x: x.strftime("%Y-%m-%d")
    )  # correct date incase datetime.datetime is in wrong format
    time_dict["time"] = pd.to_datetime(time_dict["date"]).apply(
        lambda x: x.timestamp() * 1000
    )  # milli seconds

    hist_dict = time_dict.drop(["date"], axis=1)
    hist_dict["MA_5"] = hist_dict["close"].rolling(window=5, min_periods=1).mean()
    hist_dict["MA_20"] = hist_dict["close"].rolling(window=20, min_periods=1).mean()

    history = hist_dict.to_dict(orient="dict")
    return history


def _calc_performance(history):
    """
    Calculate performance metrics and moving averages based on historical data.

    Parameters:
        history (list of dict): Historical data with 'close' prices.

    Returns:
        dict: Performance metrics and moving averages.
    """

    hist_df = pd.DataFrame().from_dict(history)

    closes = hist_df["close"].tolist()

    perf = {}
    try:
        perf["1y"] = (closes[-1] - closes[0]) / closes[0]

        if len(closes) >= 126:
            perf["6m"] = (closes[-1] - closes[-126]) / closes[-126]

        if len(closes) >= 63:
            perf["3m"] = (closes[-1] - closes[-63]) / closes[-63]

        if len(closes) >= 21:
            perf["1m"] = (closes[-1] - closes[-21]) / closes[-21]

        if len(closes) >= 5:
            perf["1w"] = (closes[-1] - closes[-5]) / closes[-5]
    except IndexError:
        raise ValueError("Not enough data points to calculate all performance metrics.")

    moving_averages = {
        "MA_5": sum(closes[-5:]) / 5 if len(closes) >= 5 else None,
        "MA_20": sum(closes[-20:]) / 20 if len(closes) >= 20 else None,
        "MA_50": sum(closes[-50:]) / 50 if len(closes) >= 50 else None,
        "MA_100": sum(closes[-100:]) / 100 if len(closes) >= 100 else None,
        "MA_200": sum(closes[-200:]) / 200 if len(closes) >= 200 else None,
    }
    for key, val in moving_averages.items():
        moving_averages[key] = format_price(val)

    for key, val in perf.items():
        perf[key] = format_percent(val)

    return {"performance": perf, "moving_averages": moving_averages}


def history_to_plotly_candle(history):
    hist_df = pd.DataFrame().from_dict(history)

    hist_df["dates"] = hist_df["time"].apply(
        lambda row: datetime.fromtimestamp(int(row) / 1000).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    )
    chart_data = {
        "dates": hist_df["dates"].tolist(),
        "closes": hist_df["close"].tolist(),
        "highs": hist_df["high"].tolist(),
        "lows": hist_df["low"].tolist(),
        "opens": hist_df["open"].tolist(),
        "MA_5": hist_df["MA_5"].tolist(),
        "MA_20": hist_df["MA_20"].tolist(),
    }

    return chart_data
