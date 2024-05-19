from math import isnan

"""
Extra assertions for unittests
"""

try:
    from fin.seq.serie import Serie
except:
    pass

class ExtraTests:
    def assertSerieEqual(self, actual, expected, *args, **kwargs):
        """ Assert that two series are identical.

            Perform basic tests and then examine the series data row-by-row
            to pin-point the differences.
        """
        self.assertIsInstance(actual, Serie)
        self.assertEqual(actual.headings, expected.headings, *args, **kwargs)
        for n, (a, b) in enumerate(zip(actual.rows, expected.rows)):
            self.assertEqual(a, b, msg=f"First differing row: {n}")

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

    def assertStartsWith(self, actual, head, msg=None):
        if msg is None:
            msg = f"{actual!r} does not start with {head!r}"
        
        tmp = self.longMessage
        try:
            self.longMessage = False
            return self.assertTrue(actual.startswith(head), msg=msg)
        finally:
            self.longMessage = tmp


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
