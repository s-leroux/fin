import unittest

from fin.utils import formatters
from fin.utils import termcap

class TestContext(unittest.TestCase):
    def test_default_init(self):
        context = formatters.Context()

        self.assertTrue(context['termcap'])

class TestFloatFormatter(unittest.TestCase):
    def test_format_number(self):
        number = 1.2345
        context = formatters.Context()
        formatter = formatters.FloatFormatter(precision=3)

        actual = formatter(context, number)

        self.assertEqual(actual[0], "1")
        self.assertEqual(actual[1], ".")
        self.assertEqual(actual[2], "234")

class TestComposite(unittest.TestCase):
    def test_float_plus_red(self):
        number = 1.2345
        context = formatters.Context(termcap=termcap.ANSITerminalTermCap())
        formatter = formatters.FloatFormatter()
        composite = formatter + formatters.Red()

        actual = composite(context, number)

        self.assertEqual(actual[0], "\x1b[31;1m1\x1b[0m")
        self.assertEqual(actual[1], "\x1b[31;1m.\x1b[0m")
        self.assertEqual(actual[2], "\x1b[31;1m23\x1b[0m")


