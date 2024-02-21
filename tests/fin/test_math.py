import unittest

import fin.math
import builtins

# ======================================================================
# Constants
# ======================================================================
class TestMathConstants(unittest.TestCase):
    def test_epsilon_defined(self):
        self.assertEqual(fin.math.EPSILON, 0.0001)

# ======================================================================
# Statistical functions
# ======================================================================
class TestMathStatisticalFunctions(unittest.TestCase):
    def round(self, x, n=3):
        return builtins.round(x, n)

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

    def test_cdf_table(self):
        # t = [(x/100, round(cdf(x/100), 5)) for x in range(0,500,10)]
        # Table from https://en.wikipedia.org/wiki/Standard_normal_table
        table = [(0.0, 0.5),
         (0.1, 0.53983),
         (0.2, 0.57926),
         (0.3, 0.61791),
         (0.4, 0.65542),
         (0.5, 0.69146),
         (0.6, 0.72575),
         (0.7, 0.75804),
         (0.8, 0.78814),
         (0.9, 0.81594),
         (1.0, 0.84134),
         (1.1, 0.86433),
         (1.2, 0.88493),
         (1.3, 0.9032),
         (1.4, 0.91924),
         (1.5, 0.93319),
         (1.6, 0.9452),
         (1.7, 0.95543),
         (1.8, 0.96407),
         (1.9, 0.97128),
         (2.0, 0.97725),
         (2.1, 0.98214),
         (2.2, 0.9861),
         (2.3, 0.98928),
         (2.4, 0.9918),
         (2.5, 0.99379),
         (2.6, 0.99534),
         (2.7, 0.99653),
         (2.8, 0.99744),
         (2.9, 0.99813),
         (3.0, 0.99865),
         (3.1, 0.99903),
         (3.2, 0.99931),
         (3.3, 0.99952),
         (3.4, 0.99966),
         (3.5, 0.99977),
         (3.6, 0.99984),
         (3.7, 0.99989),
         (3.8, 0.99993),
         (3.9, 0.99995),
         (4.0, 0.99997),
         (4.1, 0.99998),
         (4.2, 0.99999),
         (4.3, 0.99999),
         (4.4, 0.99999),
         (4.5, 1.0),
         (4.6, 1.0),
         (4.7, 1.0),
         (4.8, 1.0),
         (4.9, 1.0)]

        for x, expected in table:
            self.assertEqual(self.round(fin.math.cdf(x), 5), expected)

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
