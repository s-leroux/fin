import unittest
import os

from testing import mock
from fin import requests

class TestUtilities(unittest.TestCase):
    def test_get(self):
        """ The get() method should insert a well known user agent in the headers
        """
        get = mock.MockFunction(lambda url, *args, headers, **kwargs: None)

        r = requests.get("http://www.google.com", _get=get)
        self.assertTrue(get.called)
        self.assertRegex(get.call_args['headers']['User-Agent'], "Mozilla")
