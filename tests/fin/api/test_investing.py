import unittest
import os

from fin.api import investing

class TestInvesting(unittest.TestCase):
    def test_get_index_component_uri(self):
        expected = "https://www.investing.com/indices/nasdaq-composite-components"
        actual = investing.get_index_components_uri("Nasdaq Composite")
        self.assertEqual(actual, expected)

    if os.environ.get('SLOW_TESTS'):
        def test_fetch_index_components(self):
            actual = investing.fetch_index_components("Nasdaq Composite")
