import unittest

import fin.math

class TestMathConstants(unittest.TestCase):
    def test_epsilon_defined(self):
        self.assertEqual(fin.math.EPSILON, 0.0001)
