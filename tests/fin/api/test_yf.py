import unittest

from fin.api.yf import Client
from tests.fin.api import HistoricalDataTest

class TestYF(HistoricalDataTest, unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.ticker = "MCD"
