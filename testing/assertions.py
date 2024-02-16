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
            test(a, b, msg)

    def assertFloatSequenceEqual(self, actual, expected, msg=None):
        return self.assertSequencePass(self.assertFloatEqual, actual, expected, msg)

    def assertIterableEqual(self, actual, expected, msg=None):
        """
        Compare two iterables.
        """
        return self.assertSequenceEqual(list(iter(actual)), list(iter(expected)), msg)
