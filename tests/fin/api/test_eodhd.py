import unittest

from fin.api.eodhd import Client
from tests.fin.api import HistoricalDataTest

class TestEODHD(HistoricalDataTest, unittest.TestCase):
    def setUp(self):
        self.client = Client("demo")
        self.ticker = "MCD.US"
