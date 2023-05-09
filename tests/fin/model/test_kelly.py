import unittest

from fin.model import kelly

# ======================================================================
# elly Criterion
# ======================================================================
class TestKellyCriterion(unittest.TestCase):
    def test_f_star(self):
        """
        It should find the optimum allocation according to the Kelly Criterion.

        Example from https://blogs.cfainstitute.org/investor/2018/06/14/the-kelly-criterion-you-dont-know-the-half-of-it/
        """
        WIN=0.20
        LOSS=0.20
        WIN_PROB=0.60

        EXPECTED=1.00

        model = kelly.KellyCriterion(dict(
            p=WIN_PROB,
            a=WIN,
            b=LOSS,
            ))

        f_star = model['f_star']
        self.assertAlmostEqual(f_star, EXPECTED, places=3)

    def test_no_risk(self):
        """
        Edge case: the Kelly Criterion should stand for riskless investiments.
        """
        WIN=0.20
        LOSS=0.20
        WIN_PROB=1.00

        EXPECTED=5.00

        model = kelly.KellyCriterion(dict(
            p=WIN_PROB,
            a=WIN,
            b=LOSS,
            ))

        f_star = model['f_star']
        self.assertAlmostEqual(f_star, EXPECTED, places=3)

    def test_no_gain(self):
        """
        Edge case: the Kelly Criterion should stand for riskfull investiments.
        """
        WIN=0.20
        LOSS=0.20
        WIN_PROB=0.00

        EXPECTED=-5.00

        model = kelly.KellyCriterion(dict(
            p=WIN_PROB,
            a=WIN,
            b=LOSS,
            ))

        f_star = model['f_star']
        self.assertAlmostEqual(f_star, EXPECTED, places=3)

