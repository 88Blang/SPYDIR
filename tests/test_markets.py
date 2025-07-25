import unittest
from SPYDIR.markets.market import Market
import types


class Test_Markets(unittest.TestCase):
    """
    TODO
    - complete tests
    """

    def test_get_erp(self):
        data = Market.get_erp()
        self.assertIsInstance(data, float)

    def test_get_forex_rates(self):
        data = Market.forex()
        self.assertIsInstance(data, dict)

        for key, value in data.items():
            with self.subTest(key=key):
                self.assertTrue(
                    key.startswith("USD_") or key.startswith("GBP_"),
                    msg=f"Invalid key prefix: {key}",
                )
                self.assertIsInstance(
                    value,
                    (float, int),
                    msg=f"Value for {key} is not a float: {value} ({type(value)})",
                )

    def test_forex_rate_pair(self):

        pairs = ["USD_CAD", "USD_GBP", None, "22"]

        for pair in pairs:

            try:
                data = Market.forex(pair)
                self.assertIsInstance(data, float)
            except NameError:
                continue

    def test_get_interest_rate(self):

        for t in [1 / 24, 5 / 12, 2, 6, 35]:
            data = Market.rate(t=t)
            self.assertIsInstance(data, float)
