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
        self._log = log.Logging(self._stream, log_level=4)

    def test_error(self):
        MSG = "This is my message!"
        self._log.error(MSG)
        actual = self._stream.getvalue()
        self.assertIn(MSG, actual)
        self.assertTrue(actual.startswith("E:"))

    def test_warn(self):
        MSG = "This is my message!"
        self._log.warn(MSG)
        actual = self._stream.getvalue()
        self.assertIn(MSG, actual)
        self.assertTrue(actual.startswith("W:"))

    def test_info(self):
        MSG = "This is my message!"
        self._log.info(MSG)
        actual = self._stream.getvalue()
        self.assertIn(MSG, actual)
        self.assertTrue(actual.startswith("I:"))

class TestConsole(unittest.TestCase):
    def test_console_is_defined(self):
        console = log.console
        self.assertIsInstance(console, log.Logging)
        self.assertIs(console._ostream, sys.stderr)
