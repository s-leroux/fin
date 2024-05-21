import os
import unittest

from fin.api import binance
from fin.api.binance import Client

from tests.fin.api import HistoricalDataTest
from fin.datetime import CalendarDate, CalendarDateDelta, parseisodate

class TestBinancePrivate(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_historical_data_download(self):
        # Checked with https://data.binance.vision/?prefix=data/spot/daily/klines/BTCUSDT/1d/
        res = binance.historical_data_download("BTCUSDT", {'days': 5}, "2024-05-15")
        expected = \
            [[1715385600.000,
              '60799.99000000',
              '61515.00000000',
              '60487.09000000',
              '60825.99000000',
              '13374.56936000',
              1715471999.999,
              '814928013.45732880',
              753281,
              '6223.09555000',
              '379263096.21513300',
              '0'],
             [1715472000.000,
              '60825.99000000',
              '61888.00000000',
              '60610.00000000',
              '61483.99000000',
              '12753.13236000',
              1715558399.999,
              '781041632.46238350',
              727113,
              '6416.91108000',
              '393132351.88839250',
              '0'],
             [1715558400.000,
              '61484.00000000',
              '63450.00000000',
              '60749.21000000',
              '62940.08000000',
              '32733.41839000',
              1715644799.999,
              '2041896626.61081470',
              1371433,
              '16717.90863000',
              '1043060982.35746010',
              '0'],
             [1715644800.000,
              '62940.09000000',
              '63118.36000000',
              '61142.77000000',
              '61577.49000000',
              '29088.72041000',
              1715731199.999,
              '1800171876.16766540',
              1127939,
              '13815.81443000',
              '855088066.21248800',
              '0'],
             [1715731200.000,
              '61577.49000000',
              '66444.16000000',
              '61319.47000000',
              '66206.50000000',
              '43559.74719000',
              1715817599.999,
              '2794259631.89104640',
              1729454,
              '21797.84094000',
              '1398781701.44138860',
              '0']]

        self.assertSequenceEqual(res, expected)

class TestBinance(HistoricalDataTest, unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.ticker = "BTCUSDT"

    if os.environ.get('SLOW_TESTS'):
        pass
