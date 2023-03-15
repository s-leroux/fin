import unittest

from fin.utils import termcap

STR = "Hello World"

# ======================================================================
# Default terminal capabilities
# ======================================================================
class TestTermCap(unittest.TestCase):
    def test_colors(self):
        tc = termcap.TermCap()

        for color in ["red", "yellow", "green"]:
            with self.subTest(color=color):
                self.assertEqual(STR, getattr(tc, color)(STR))

# ======================================================================
# ANSI terminal capabilities
# ======================================================================
class TestANSITerminalTermCap(unittest.TestCase):
    def test_red(self):
        tc = termcap.ANSITerminalTermCap()

        for color in ["red", "yellow", "green"]:
            with self.subTest(color=color):
                self.assertIn(STR, getattr(tc, color)(STR))
