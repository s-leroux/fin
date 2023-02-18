import unittest

from fin.model import rates

# ======================================================================
# Interest rates
# ======================================================================
class TestInterestRates(unittest.TestCase):
    def test_continuous_compounding(self):
        """
        It should convert from discrete compound interest rates to
        continuous compound interest rates.

        Example from John C. Hull
        "Options, Futures and Other Derivatives, 5th ed", p44
        """
        YEARLY_RATE=0.10 # 10% par annum interest rates
        FREQUENCY=2      # Semiannual compounding
        CONTINUOUS_RATE=0.09758

        actual = rates.continuous_compounding(YEARLY_RATE, FREQUENCY)
        self.assertAlmostEqual(actual, CONTINUOUS_RATE, places=4)

    def test_discrete_compounding(self):
        """
        It should convert from continuous compound interest rates to
        discrete compound interest rates.

        Example from John C. Hull
        "Options, Futures and Other Derivatives, 5th ed", p44
        """
        YEARLY_RATE=0.0808 # 10% par annum interest rates
        FREQUENCY=4      # Semiannual compounding
        CONTINUOUS_RATE=0.08

        actual = rates.discrete_compounding(CONTINUOUS_RATE, FREQUENCY)
        self.assertAlmostEqual(actual, YEARLY_RATE, places=4)

    def test_model_solver(self):
        """
        It should convert from continuous compound interest rates to
        discrete compound interest rates.

        Example from John C. Hull
        "Options, Futures and Other Derivatives, 5th ed", p44
        """
        YEARLY_RATE=0.0808 # 10% par annum interest rates
        FREQUENCY=4      # Semiannual compounding
        CONTINUOUS_RATE=0.08
        
        model = rates.Rates(dict(rc=CONTINUOUS_RATE, rm=YEARLY_RATE))
        actual = model['m']
        self.assertAlmostEqual(actual, FREQUENCY, places=1)

