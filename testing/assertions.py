from math import isnan

"""
Extra assertions for unittests
"""

class ExtraTests:
    def assertFloatEqual(self, actual, expected, msg=None):
        """
        Assert that two floats are equal or both NaN.
        """
        if isnan(actual) and isnan(expected):
            return

        self.assertEqual(actual, expected, msg)

    def assertSequencePass(self, test, actual, expected, msg=None):
        for a, b in zip(actual, expected):
            test(self, a, b, msg)

    def assertSequenceTrue(self, test, actual, expected, msg=None):
        for a, b in zip(actual, expected):
            self.assertTrue(test(a, b), msg)

    def assertFloatSequenceEqual(self, actual, expected, msg=None, *, ndigits=8):
        return self.assertSequencePass(assertAlmostEqual(ndigits=ndigits), actual, expected, msg)

    def assertIterableEqual(self, actual, expected, msg=None):
        """
        Compare two iterables.
        """
        return self.assertSequenceEqual(list(iter(actual)), list(iter(expected)), msg)


def assertAlmostEqual(*, ndigits=8):
    def _assertAlmostEqual(self, actual, expected, msg=None):
        if actual is not None and expected is not None:
            if isnan(actual) and isnan(expected):
                return

            if ndigits is not None:
                actual = round(actual, ndigits)
                expected = round(expected, ndigits)

        self.assertEqual(actual, expected, msg)

    return _assertAlmostEqual
