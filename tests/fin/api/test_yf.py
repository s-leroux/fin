import unittest
import os

from testing import mock
from fin.api import yf

class TestUtilities(unittest.TestCase):
    def test_get(self):
        """ The get() method should insert a well known user agent in the headers
        """
        get = mock.MockFunction(lambda url, *args, headers, **kwargs: None)

        r = yf.get("http://www.google.com", _get=get)
        self.assertTrue(get.called)
        self.assertRegex(get.call_args['headers']['User-Agent'], "Mozilla")

class TestYF(unittest.TestCase):
    if os.environ.get('SLOW_TESTS'):
        def test_historical_data(self):
            t = yf.historical_data("^FCHI")
            self.assertSequenceEqual(t.names(), ('#', 'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'))
