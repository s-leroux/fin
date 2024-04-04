import unittest

from . import tuplex

class TupleTest(unittest.TestCase):
    def test_from_doubles(self):
        t = tuplex.test_from_doubles()
        self.assertIsInstance(t, tuple)
        self.assertSequenceEqual(t, tuple(range(1000)))
