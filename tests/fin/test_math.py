import unittest

import fin.math

class TestMathConstants(unittest.TestCase):
    def test_epsilon_defined(self):
        self.assertEqual(fin.math.EPSILON, 0.0001)

class TestMathRoot(unittest.TestCase):
    def test_root_lin1(self):
        def f(x):
            return 2*x+3 # root is -1.5

        actual = fin.math.solve(f, 'x', -10, +10)
        self.assertAlmostEqual(actual, -1.5, delta=fin.math.EPSILON)

    def test_root_quad1(self):
        def f(x):
            return 2*(x-1)*(x-1)-8 # roots are -1 and 3

        actual = fin.math.solve(f, 'x', 0, +10)
        self.assertAlmostEqual(actual, 3, delta=fin.math.EPSILON)
