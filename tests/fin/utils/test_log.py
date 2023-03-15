import unittest
import io
import sys

from fin.utils import log

# ======================================================================
# Logging facilities
# ======================================================================
class TestLogging(unittest.TestCase):
    def setUp(self):
        self._stream = io.StringIO()
        self._log = log.Logging(self._stream)

    def test_error(self):
        MSG = "This is my message!"
        CODE = "T00001"
        self._log.error(CODE, MSG)
        actual = self._stream.getvalue()
        self.assertIn(MSG, actual)
        self.assertTrue(actual.startswith("E"+CODE))

    def test_warn(self):
        MSG = "This is my message!"
        CODE = "T00001"
        self._log.warn(CODE, MSG)
        actual = self._stream.getvalue()
        self.assertIn(MSG, actual)
        self.assertTrue(actual.startswith("W"+CODE))

    def test_info(self):
        MSG = "This is my message!"
        CODE = "T00001"
        self._log.info(CODE, MSG)
        actual = self._stream.getvalue()
        self.assertIn(MSG, actual)
        self.assertTrue(actual.startswith("I"+CODE))

class TestConsole(unittest.TestCase):
    def test_console_is_defined(self):
        console = log.console
        self.assertIsInstance(console, log.Logging)
        self.assertIs(console._ostream, sys.stderr)
