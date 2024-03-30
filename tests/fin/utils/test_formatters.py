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

        text, llen, rlen = formatter(context, number)

        self.assertEqual(text, "1.234")
        self.assertEqual(llen, 1)
        self.assertEqual(rlen, 4)

    def test_format_number_zero_prec(self):
        number = 1.2345
        context = formatters.Context()
        formatter = formatters.FloatFormatter(precision=0)

        text, llen, rlen = formatter(context, number)

        self.assertEqual(text, "1")
        self.assertEqual(llen, 1)
        self.assertEqual(rlen, 0)

    def test_format_none(self):
        context = formatters.Context()
        formatter = formatters.FloatFormatter(precision=3)

        text, llen, rlen = formatter(context, None)

        self.assertEqual(text, "None")
        # llen and rlen are undefined in this case
        # self.assertEqual(llen, 0)
        # self.assertEqual(rlen, 0)

class TestComposite(unittest.TestCase):
    def test_float_plus_red(self):
        number = 1.2345
        context = formatters.Context(termcap=termcap.ANSITerminalTermCap())
        formatter = formatters.FloatFormatter()
        composite = formatter + formatters.Red()

        text, llen, rlen = composite(context, number)

        self.assertEqual(text, "\x1b[31;1m1.23\x1b[0m")
        self.assertEqual(llen, 1)
        self.assertEqual(rlen, 3)


