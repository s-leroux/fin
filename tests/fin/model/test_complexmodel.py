import unittest

from fin.model import complexmodel
from fin.utils import termcap

# ======================================================================
# Core complex model behavior
# ======================================================================
class TestComplexModel(unittest.TestCase):
    def setUp(self):
        self._eq_A = lambda x : x*x - 12*x + 32 # roots x=4 and x=8
        self._params_A = (
                dict(name="x", description="The X param for parabola"),
                )

        self._eq_B = lambda a, b : (a-10)*(a-10)+(b-2)(b-2)-8 # roots (8,0) and (12,0)
        self._params_B = (
                dict(name="a", description="The A param for circle"),
                dict(name="b", description="The B param for circle"),
                )

        self._model = complexmodel.ComplexModel()

    def test_basic_workflow(self):
        self._model.register(self._eq_A, *self._params_A)
        self._model.register(self._eq_B, *self._params_B)

        sig_X = (self._eq_A, "x")
        sig_A = (self._eq_B, "a")
        sig_B = (self._eq_B, "b")
        self.assertEqual(len(self._model._domains), 3)
        self.assertEqual(self._model.get_domain_for(*sig_X), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(self._model.get_domain_for(*sig_A), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(self._model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)

        self._model.bind(*sig_X, *sig_A)
        self.assertEqual(len(self._model._domains), 2)
        self.assertEqual(self._model.get_domain_for(*sig_X), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(self._model.get_domain_for(*sig_A), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(self._model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)

        REDUCED_DOMAIN=(1,50)
        self._model.domain(*sig_A, *REDUCED_DOMAIN)
        self.assertEqual(len(self._model._domains), 2)
        self.assertEqual(self._model.get_domain_for(*sig_X), REDUCED_DOMAIN)
        self.assertEqual(self._model.get_domain_for(*sig_A), REDUCED_DOMAIN)
        self.assertEqual(self._model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)

        REDUCED_DOMAIN_2=(2,75)
        self._model.domain(*sig_X, *REDUCED_DOMAIN_2)
        self.assertEqual(len(self._model._domains), 2)
        self.assertEqual(self._model.get_domain_for(*sig_X), (2, 50))
        self.assertEqual(self._model.get_domain_for(*sig_A), (2, 50))
        self.assertEqual(self._model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)
        print(self._model)
