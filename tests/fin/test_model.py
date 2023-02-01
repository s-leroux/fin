import unittest

import fin.model.turbo as turbo
import fin.math

class TestModelTurbo(unittest.TestCase):
    def test_turbo_call(self):
        TURBO_PRICE=0.60
        ASSET_PRICE=3250
        EXPECTED_ASSET_PRICE=3200
        PARITY=100
        PREMIUM=0.10

        actual = turbo.call(TURBO_PRICE,ASSET_PRICE,EXPECTED_ASSET_PRICE,PARITY,PREMIUM)

        self.assertAlmostEqual(actual, 0.0, delta=fin.math.EPSILON)

    def test_turbo_put(self):
        TURBO_PRICE=0.60
        ASSET_PRICE=3250
        EXPECTED_ASSET_PRICE=3300
        PARITY=100
        PREMIUM=0.10

        actual = turbo.put(TURBO_PRICE,ASSET_PRICE,EXPECTED_ASSET_PRICE,PARITY,PREMIUM)

        self.assertAlmostEqual(actual, 0.0, delta=fin.math.EPSILON)

