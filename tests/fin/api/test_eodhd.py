import unittest
import os

from fin.api.eodhd import Client

class TestYF(unittest.TestCase):
    if os.environ.get('SLOW_TESTS'):
        def test_historical_data(self):
            client = Client("demo")
            t = client.historical_data("MCD.US")
            self.assertSequenceEqual(t.names(), ('Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'))
