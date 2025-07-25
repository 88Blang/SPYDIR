from yahooquery import Ticker
from .utils.format_helpers import *


def get_related(ticker):

    methods = {"YQ": fetch_related_yq}

    for key, method in methods.items():
        try:
            related = method(str(ticker))
            if related:
                return related
        except RuntimeError as e:  # If API fails, continue to next
            continue
    return None


def fetch_related_yq(ticker):
    yq_tick = Ticker(ticker)
    related_tick = yq_tick.recommendations

    related_tickers = [
        rec["symbol"] for rec in related_tick[ticker]["recommendedSymbols"]
    ]

    tickers = [ticker] + related_tickers
    yq_ticks = Ticker(" ".join(tickers))

    fin_query = yq_ticks.financial_data
    if isinstance(fin_query, str):
        return {}

    related_dicts = []
    for tick in tickers:
        tick_query = fin_query[tick]
        if not isinstance(tick_query, str):
            tick_dict = {
                "Ticker": tick,
                "Price": format_currency(tick_query.get("currentPrice", "")),
                "Recommendation": str(
                    format_number(tick_query.get("recommendationMean", "NA"))
                )
                + " - "
                + tick_query.get("recommendationKey", "").replace("_", " ").title(),
                "Revenue": format_number(tick_query.get("totalRevenue", 0)),
                "Profit Margin": format_pct(tick_query.get("profitMargins", "-")),
                "ROA": format_pct(tick_query.get("returnOnAssets", "-")),
                "ROE": format_pct(tick_query.get("returnOnEquity", "-")),
            }
            related_dicts.append(tick_dict)

    return related_dicts
