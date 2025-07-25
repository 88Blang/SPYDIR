import unittest
from SPYDIR.stock_client import stock_client
from SPYDIR.data import cache


class Test_Reports(unittest.TestCase):
    """
    TODO
    - complete tests
    """

    def test_get_report(self):
        test_ticker = "MSFT"
        stock_obj = stock_client(ticker=test_ticker, cache=cache, arg="report")
        report_args = [
            "news",
            "wiki",
            "related",
            "history",
            "statements",
        ]
        self.assertIsInstance(stock_obj, dict)

        for key in report_args:
            self.assertTrue(key in stock_obj.keys(), msg=f"Key: {key} not in stock_obj")

        for key in report_args:
            data = cache.get(f"{test_ticker}_{key}")
            self.assertTrue(data is None)

        for key in ["moving_averages", "performance"]:
            self.assertTrue(
                key in stock_obj["performance"].keys(),
                msg=f"Key: {key} not in stock_obj.performance",
            )

    def test_structure(self):

        stock_obj = stock_client(ticker="AAPL", arg="report")

        report_args = [
            "news",
            "wiki",
            "related",
            "history",
            "statements",
        ]
        print(stock_obj.keys())
        for arg in report_args:
            self.assertTrue(arg in stock_obj.keys())
