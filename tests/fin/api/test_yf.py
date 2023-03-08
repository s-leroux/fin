import unittest
import os

from fin.api import yf

class TestYF(unittest.TestCase):
    if os.environ.get('SLOW_TESTS'):
        def test_historical_data(self):
            t = yf.historical_data("^FCHI")
            self.assertSequenceEqual(t.names(), ('Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'))
