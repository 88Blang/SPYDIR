from SPYDIR.stock_client import stock_client
import pandas as pd
from SPYDIR.utils.helpers import get_img
from SPYDIR.financial.helpers import nasdaq_IS_summary
from SPYDIR.pdf.get_report import get_report
from SPYDIR.excel.get_excel import get_excel
from SPYDIR.stock_client import Field


class Stock:

    def __init__(self, ticker, arg=None):
        self.ticker = ticker
        stock_client(ticker, arg=arg or Field.BASE)

    def get_dict(self) -> dict:
        return stock_client(self.ticker)

    def get_info(self) -> pd.DataFrame:
        stock_dict = self.get_dict()
        info_df = pd.DataFrame.from_dict(stock_dict.get("info", ""), orient="index")
        info_df = info_df.rename(columns=info_df.loc["Name"]).drop("Name")
        return info_df

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
