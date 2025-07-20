import unittest
from SPYDIR.history import get_history, history_to_plotly_candle
from SPYDIR.stock_client import stock_client
import pandas as pd


class Test_History(unittest.TestCase):
    """
    TODO
    - complete tests
    """

    def test_get_history(self):

        ticker = "NVDA"
        history = get_history(ticker)
        self.assertIsInstance(history, dict)
        hist_df = pd.DataFrame.from_dict(history)
        self.assertIsInstance(hist_df, pd.DataFrame)

        hist_data = stock_client(ticker=ticker, arg="history")
        self.assertIsInstance(hist_data, dict)

    def test_history_to_plotly_candle(self):

        ticker = "NVDA"
        history = get_history(ticker)
        self.assertIsInstance(history, dict)

        hist_plotly = history_to_plotly_candle(history)

        self.assertIsInstance(hist_plotly, dict)
