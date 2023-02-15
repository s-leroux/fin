import unittest

import fin.math
import builtins

class TestMathConstants(unittest.TestCase):
    def test_epsilon_defined(self):
        self.assertEqual(fin.math.EPSILON, 0.0001)

class TestMathNorm(unittest.TestCase):
    def round(self, x):
        return builtins.round(x, 3)

    def test_cdf(self):
        """ cdf() should return the cumulative distribution for the
            standard normal distribution.
        """
        it = iter([
            -3.0, 0.001,
            -2.7, 0.003,
            -2.2, 0.014,
            -1.7, 0.045,
            -1.3, 0.097,
            -0.9, 0.184,
            -0.4, 0.345,
            -0.1, 0.460,
        ])

        for x in it:
            expected = next(it)
            self.assertEqual(self.round(fin.math.cdf(x)), expected)

    def test_cdf_mu_and_sigma(self):
        """ cdf() should return the cumulative distribution for a
            custom normal distribution.
        """
        d = dict(mu=0.15, sigma=0.30)
        it = iter([
            +0.65, 0.952
        ])

        for x in it:
            expected = next(it)
            self.assertEqual(self.round(fin.math.cdf(x, **d)), expected)

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
