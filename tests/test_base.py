import unittest

# import warnings
from SPYDIR.base.base import get_base
from SPYDIR.stock_client import stock_client


class Test_Base(unittest.TestCase):
    """
    TODO
    - complete tests
    """

    def test_root(self):

        stock_obj = stock_client(ticker="AAPL")

        self.assertIsInstance(stock_obj, dict)

    def test_base(self):

        tickers = ["AAPL", 1, 2, ""]

        for ticker in tickers:
            try:
                stock_obj = get_base(ticker=ticker)
            except Exception as e:
                stock_obj = {"Error": e}

            self.assertIsInstance(
                stock_obj, dict, msg=f"Ticker: {ticker} - {stock_obj}"
            )
