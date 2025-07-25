from SPYDIR.stock_client import stock_client
import pandas as pd
from SPYDIR.utils.helpers import get_img
from SPYDIR.utils.format_helpers import *
from SPYDIR.financial.helpers import nasdaq_IS_summary
from SPYDIR.pdf.get_report import get_report
from SPYDIR.excel.get_excel import get_excel
from SPYDIR.stock_client import Field

keys = {}
keys["info"] = [
    "name",
    "ticker",
    "sector",
    "industry",
    "exchange",
    "price",
    "average_volume",
    "market_cap",
    "pe_ratio",
    "pb_ratio",
    "beta",
    "dividend_yield",
]
keys["ratios"] = [
    "return_on_assets",
    "return_on_equity",
    "earnings_growth",
    "revenue_growth",
    "gross_margin",
    "ebitda_margin",
    "operating_margin",
    "profit_margin",
]
keys["metrics"] = ["revenue", "ebitda", "gross_profits"]
keys["shares"] = [
    "outstanding",
    "float",
    "shares_insider_pct",
    "shares_institutions_pct",
    "shares_short",
    "short_prev_month",
    "short_ratio",
    "short_pct",
]
keys["esg"] = [
    "audit_risk",
    "board_risk",
    "compensation_risk",
    "shareholder_risk",
    "overall_risk",
    "employee_count",
]


def get_section_info(section, context):
    """
    TODO
    - Capm - erp/beta/rfr
    - performance (year, perf, ma)

    """
    if section in ["metrics", "ratios"]:
        section_dict = {
            key: context["financial"][section].get(key, None) for key in keys[section]
        }
    # elif section == "esg":
    #     section_dict = {key: context[section].get(key, None) for key in keys[section]}
    elif section == "info":
        section_dict = {key: context.get(key, None) for key in keys[section]}
    else:
        section_dict = {key: context[section].get(key, None) for key in keys[section]}

    section_df = (
        pd.DataFrame.from_dict(section_dict, orient="index")
        .dropna(axis=0)
        .apply(add_format, axis=1)
    )
    section_df.index = section_df.index.map(format_title)  # format index names

    if section == "info":
        section_df = section_df.rename(columns=section_df.loc["Name"]).drop("Name")
    else:
        section_df = section_df.rename(columns={0: section.title()})
    return section_df


class Stock:

    def __init__(self, ticker, arg=None):
        self.ticker = ticker
        stock_client(ticker, arg=arg or Field.BASE)

    def get_dict(self) -> dict:
        return stock_client(self.ticker)

    @property
    def info(self):
        return get_section_info(section="info", context=stock_client(self.ticker))

    @property
    def metrics(self):
        return get_section_info(section="metrics", context=stock_client(self.ticker))

    @property
    def ratios(self):
        return get_section_info(section="ratios", context=stock_client(self.ticker))

    @property
    def shares(self):
        return get_section_info(section="shares", context=stock_client(self.ticker))

    @property
    def esg(self):
        return get_section_info(section="esg", context=stock_client(self.ticker))

    def get_history(self) -> pd.DataFrame:
        hist = stock_client(self.ticker, arg="history")
        return pd.DataFrame(hist)

    def get_related(self) -> pd.DataFrame:
        related = stock_client(self.ticker, arg="related")
        return pd.DataFrame(related)

    def get_news(self) -> dict:
        news = stock_client(self.ticker, arg="news")
        return news

    def get_rec_trend(self) -> pd.DataFrame:
        stock_dict = self.get_dict()
        related = stock_dict.get("analyst", {}).get("rec_trend", {})
        return pd.DataFrame(related)

    def get_statements(self) -> dict:
        statements = stock_client(self.ticker, arg="statements")
        return statements

    def get_IS(self) -> dict:
        statements = stock_client(self.ticker, arg="statements")
        return pd.DataFrame(statements.get("income_statement", {}))

    def get_BS(self) -> dict:
        statements = stock_client(self.ticker, arg="statements")
        return pd.DataFrame(statements.get("balance_sheet", {}))

    def get_CF(self) -> dict:
        statements = stock_client(self.ticker, arg="statements")
        return pd.DataFrame(statements.get("cash_flow", {}))

    ###### Model_df, inputs, is summary

    def get_IS_summary(self) -> dict:
        statements = stock_client(self.ticker, arg="statements")
        is_summary, growths = nasdaq_IS_summary(stock_statements=statements)
        return pd.DataFrame(is_summary)

    ##################################

    def get_wiki(self) -> dict:
        wiki = stock_client(self.ticker, arg="wiki")
        return wiki

    def img(self):
        wiki = self.get_wiki()
        img_url = wiki.get("img", "")
        buffer = get_img(img_url)
        return buffer

    def get_all(self) -> dict:
        return stock_client(self.ticker, arg="report")

    def create_report(self, output: str = None):
        get_report(self.ticker, output=output or f"{self.ticker}_Report.pdf")

    def create_excel(self, output: str = None):
        get_excel(self.ticker, output=output or f"{self.ticker}_Sheet.xlsm")
