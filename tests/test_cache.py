import unittest
from SPYDIR.data import cache


class Test_Cache(unittest.TestCase):
    """
    TODO
    - complete tests
    """

    def test_init_cache(self):

        self.assertIsInstance(cache._cache_dict, dict)

        cache.set("MY_KEY", "MY_VAL", timeout=0)
        self.assertIsInstance(cache._cache_dict, dict)

        item = cache.get("MY_KEY")
        self.assertEqual(item, "MY_VAL")

        cache.delete("MY_KEY")
        self.assertIsInstance(cache._cache_dict, dict)

        self.assertEqual("MY_KEY" not in cache._cache_dict.keys(), True)
