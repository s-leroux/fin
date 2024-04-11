import unittest
import random

from fin.seq.fc import stat
from testing import assertions

from tests.fin.seq.fc import utilities

# ======================================================================
# Window functions
# ======================================================================
class TestStandardDeviation(unittest.TestCase, assertions.ExtraTests):
    def test_stdev_s(self):
        actual = utilities.apply(self,
            stat.stdev.s(3),
            [x**2 for x in range(10, 20)],
        )

        self.assertFloatSequenceEqual(actual.py_values, [
            None,
            None,
            22.00757445,
            24.00694344,
            26.00640947,
            28.00595175,
            30.00555504,
            32.00520791,
            34.00490161,
            36.00462933,
        ])

    def test_variance(self):
        actual = utilities.apply(self,
            stat.var.s(5),
            [x**2 for x in range(10, 20)],
        )

        self.assertFloatSequenceEqual(actual.py_values, [
            None,
            None,
            None,
            None,
            1443.5,
            1693.5,
            1963.5,
            2253.5,
            2563.5,
            2893.5,
        ])

    def test_propagate_nones(self):
        data = [x**2 for x in range(10, 20)]
        data[5] = None
        data[6] = None

        actual = utilities.apply(self,
            stat.stdev.s(3),
            data,
        )

        self.assertFloatSequenceEqual(actual.py_values, [
            None,
            None,
            22.00757445,
            24.00694344,
            26.00640947,
            None,
            None,
            None,
            None,
            36.00462933,
        ])

class TestCorrelation(unittest.TestCase, assertions.ExtraTests):
    def test_correlation_with_itself(self):
        """
        The correlation of a column against itself is 1.0.
        """
        EXPECTED = [None]*5 + [1.0]
        LEN = len(EXPECTED)
        INPUT = random.sample([*range(LEN)], LEN)
        actual = utilities.apply(self,
            stat.correlation(LEN),
            INPUT,
            INPUT
        )

        self.assertFloatSequenceEqual(actual.py_values, EXPECTED)

    def test_correlation(self):
        """
        The correlation of a column against itself is 1.0.
        """
        X = [ 4.0, 2.0, 3.0, 1.0 ]
        Y = [x*-10 for x in X]
        EXPECTED = [None, -1.0, -1.0, -1.0]
        actual = utilities.apply(self,
            stat.correlation(2),
            X,
            Y
        )

        self.assertFloatSequenceEqual(actual.py_values, EXPECTED)

class TestVolatility(unittest.TestCase, assertions.ExtraTests):
    def test_volatility(self):
        # Data from John C. Hull "Options, Futures, and Other Devicatives, 5th ed." p240
        INPUT=[
            20.00,
            20.10,
            19.90,
            20.00,
            20.50,
            20.25,
            20.90,
            20.90,
            20.90,
            20.75,
            20.75,
            21.00,
            21.10,
            20.90,
            20.90,
            21.25,
            21.40,
            21.40,
            21.25,
            21.75,
            22.00,
        ]
        WINDOW=len(INPUT)-1
        OUTPUT = [*[None]*WINDOW, 0.19302342]

        actual = utilities.apply(self, stat.volatility(WINDOW), INPUT)

        self.assertFloatSequenceEqual(actual.py_values, OUTPUT)

class TestBestFit(unittest.TestCase, assertions.ExtraTests):
    def test_best_fit(self):
        actual = utilities.apply(self,
                stat.best_fit,
                [*range(5)],
                [
                    1,
                    4,
                    4,
                    4,
                    7,
                ]
        )

        self.assertFloatSequenceEqual(actual.py_values, [
            1.6,
            2.8,
            4.0,
            5.2,
            6.4,
        ])

