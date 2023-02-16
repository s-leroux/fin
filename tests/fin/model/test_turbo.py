import unittest

import fin.model.turbo as turbo
import fin.math

class TestModelTurbo(unittest.TestCase):
    def test_call_underdefined(self):
        with self.assertRaises(fin.model.Underdefined) as cm:
            turbo.Call(dict(tp=1,ap=3250,ep=3000))

    def test_call_infer_premium(self):
        call = turbo.Call(dict(tp=3,ap=3250,ep=3000,parity=100))
        self.assertAlmostEqual(call.premium, 0.5, delta=fin.math.EPSILON)

    def test_call_adjust_price(self):
        call1 = turbo.Call(dict(tp=3,ap=3250,ep=3000,parity=100))
        call2 = call1.adjust('tp', dict(ap=3450))
        self.assertAlmostEqual(call2.tp, 5, delta=fin.math.EPSILON)

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

