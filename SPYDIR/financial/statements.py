import requests
import json
import pandas as pd
import datetime
from enum import Enum


class Statement(str, Enum):
    INCOME = "income_statement"
    BALANCE = "balance_sheet"
    CASHFLOW = "cash_flow"


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


NASDAQ_META = {
    "currency": "USD",
    "source": "NASDAQ",
    "source_link": "https://www.nasdaq.com/market-activity/stocks/{ticker}/financials",
    "scale": 1000,
    "map": {
        "income_statement": {
            "revenue": "Total Revenue",
            "cogs": "Cost of Revenue",
            "gross_profit": "Gross Profit",
            "operating_profit": "Operating Income",
            "ebit": "Earnings Before Interest and Tax",
            "interest": "Interest Expense",
            "ebt": "Earnings Before Tax",
            "tax": "Income Tax",
            "net_income": "Net Income",
        },
        "balance_sheet": {
            "current_assets": "Total Current Assets",
            "cash": "Cash and Cash Equivalents",
            "investments": "Short-Term Investments",
            "receivables": "Net Receivables",
            "inventory": "Inventory",
            "total_assets": "Total Assets",
            "payables": "Accounts Payable",
            "other_current_liabilities": "Other Current Liabilities",
            "current_liabilities": "Total Current Liabilities",
            "total_debt": "Long-Term Debt",
            "total_liabilities": "Total Liabilities",
            "total_equity": "Total Equity",
        },
        "cash_flow": {
            "cfo": "Net Cash Flow-Operating",
            "depreciation": "Depreciation",
            "cfi": "Net Cash Flows-Investing",
            "capex": "Capital Expenditures",
            "cff": "Net Cash Flows-Financing",
            "net_cash_flow": "Net Cash Flow",
        },
    },
}


def get_statements(ticker):

    if ticker.endswith(".V") or ticker.endswith(".TO"):
        statements = {"_meta": {"status": "NA"}}

        return statements
    else:

        methods = {
            "NASDAQ": fetch_nasdaq_statements,
        }

    for key, method in methods.items():
        try:
            statements = method(str(ticker))
            if statements:

                statements["_meta"] = get_meta(key, ticker)
                statements["_meta"].update({"status": ""})
                return statements
        except RuntimeError as e:  # If API fails, continue to next
            continue
    return None


def get_meta(key, ticker):

    if key == "NASDAQ":
        meta = NASDAQ_META
        meta["source_link"] = meta["source_link"].format(ticker=ticker.lower())

    meta["time"] = (str(datetime.datetime.now()),)

    return meta


def fetch_nasdaq_statements(ticker):

    smap = {
        "incomeStatementTable": "income_statement",
        "balanceSheetTable": "balance_sheet",
        "cashFlowTable": "cash_flow",
        "financialRatiosTable": "financial_ratios",
    }

    response = requests.get(
        f"https://api.nasdaq.com/api/company/{ticker}/financials?frequency=1",
        headers=headers,
    )

    response_dict = json.loads(response.text)
    data = response_dict.get("data", {"ERROR"})
    if not data:
        raise RuntimeError(f"Bad or No parameter for {ticker}")

    statements = {}

    for key, value in data["tabs"].items():

        statement = data[key]
        df = pd.DataFrame().from_records(statement["rows"])

        df.rename(
            columns={
                "value1": statement["headers"]["value1"],
                "value2": statement["headers"]["value2"],
                "value3": statement["headers"]["value3"],
                "value4": statement["headers"]["value4"],
                "value5": statement["headers"]["value5"],
            },
            inplace=True,
        )

        df.set_index(statement["headers"]["value1"], inplace=True)

        statements[smap.get(key)] = df.to_dict()

    return statements
