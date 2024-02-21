import unittest

import fin.model.option as option
import fin.math

class TestModelOption(unittest.TestCase):
    def test_option_call_pricing(self):
        """ Test call option pricing using the Black-Scholes model

            From "Derivatives Essentials: An Introduction to Forwards, Futures, Options, and Swaps"
            by Aron Gottesman, p96
        """
        STRIKE=800.0
        MATURITY=1
        RISK_FREE_RATE=0.05
        ASSET_PRICE=1000.0
        ASSET_VOLATILITY=0.25

        model = option.Call(dict(
            k=STRIKE,
            t=MATURITY,
            s_0=ASSET_PRICE,
            sigma_0=ASSET_VOLATILITY,
            r_0=RISK_FREE_RATE,
        ))
        self.assertAlmostEqual(model['f_0'], 254.13, places=2)

    def test_option_put_pricing(self):
        """ Test put option pricing using the Black-Scholes model

            From "Derivatives Essentials: An Introduction to Forwards, Futures, Options, and Swaps"
            by Aron Gottesman, p98
        """
        STRIKE=95
        MATURITY=0.25
        RISK_FREE_RATE=0.02
        ASSET_PRICE=85.0
        ASSET_VOLATILITY=0.65

        model = option.Put(dict(
            k=STRIKE,
            t=MATURITY,
            s_0=ASSET_PRICE,
            sigma_0=ASSET_VOLATILITY,
            r_0=RISK_FREE_RATE,
        ))
        self.assertAlmostEqual(model['f_0'], 16.96, places=2)

    def test_option_implied_volatility_from_call(self):
        """ Test implied volatility's derifation from Black-Scholes and a call option

            From "Options, Furtures and Other Derivatives, 5th edition"
            by John C. Hull, p250
        """
        CALL_PRICE=1.875
        STRIKE=20.0
        MATURITY=0.25
        RISK_FREE_RATE=0.10
        ASSET_PRICE=21.0

        model = option.Call(dict(
            f_0=CALL_PRICE,
            k=STRIKE,
            t=MATURITY,
            s_0=ASSET_PRICE,
            r_0=RISK_FREE_RATE,
        ))
        self.assertAlmostEqual(model['sigma_0'], 0.235, places=3)


