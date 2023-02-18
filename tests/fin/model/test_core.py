import unittest

import fin.model.core as core
import fin.math

class TestModelBreakeven(unittest.TestCase):
    def test_breakeven_point(self):
        """ It should find the sell price to reach breakeven point given a
            quantity and a buying price.
        """
        def fees(amount):
            return 12

        model = core.Breakeven(fees, dict(qty=1000, s0=1))
        self.assertAlmostEqual(model['s1'], 1.024, places=4)

    def test_adjust(self):
        def fees(amount):
            return 12

        model = core.Breakeven(fees, dict(qty=1000, s0=1))
        model = model.adjust("qty", dict(s1=1.012))
        self.assertAlmostEqual(model['qty'], 2000, places=4)
