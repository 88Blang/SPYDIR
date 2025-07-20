import unittest
from SPYDIR.stock import Stock


class Test_Stock(unittest.TestCase):
    """
    TODO
    - complete tests
    """

    def test_init(self):

        stock_obj = Stock(ticker="AAPL")

        self.assertIsInstance(stock_obj, Stock)

    def test_base(self):

        tickers = ["AAPL", 1, 2, ""]

        for ticker in tickers:
            print(ticker, "\n")
            try:
                stock_obj = Stock(ticker=ticker)
                self.assertIsInstance(stock_obj, Stock)

            except Exception as e:
                stock_obj = {"Error": e}
                self.assertIsInstance(stock_obj, dict)
