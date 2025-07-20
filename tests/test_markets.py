import unittest
from SPYDIR.markets.stats import *


class Test_Markets(unittest.TestCase):
    """
    TODO
    - complete tests
    """

    def test_get_erp(self):
        data = get_erp()
        self.assertIsInstance(data, float)

    def test_get_forex_rates(self):
        data = get_forex_rates()
        self.assertIsInstance(data, dict)

        for key, value in data.items():
            with self.subTest(key=key):
                self.assertTrue(
                    key.startswith("USD_") or key.startswith("GBP_"),
                    msg=f"Invalid key prefix: {key}",
                )
                self.assertIsInstance(
                    value,
                    float,
                    msg=f"Value for {key} is not a float: {value} ({type(value)})",
                )

    def test_get_interest_rate(self):

        for t in [1 / 24, 5 / 12, 2, 6, 35]:
            data = get_interest_rate(t=t)
            self.assertIsInstance(data, float)
