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
        my_model = self._model

        my_model.register(self._eq_A, *self._params_A)
        my_model.register(self._eq_B, *self._params_B)

        sig_X = (self._eq_A, "x")
        sig_A = (self._eq_B, "a")
        sig_B = (self._eq_B, "b")
        self.assertEqual(len(my_model._domains), 3)
        self.assertEqual(my_model.get_domain_for(*sig_X), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(my_model.get_domain_for(*sig_A), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(my_model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)

        my_model.bind(*sig_X, *sig_A)
        self.assertEqual(len(my_model._domains), 2)
        self.assertEqual(my_model.get_domain_for(*sig_X), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(my_model.get_domain_for(*sig_A), complexmodel.DEFAULT_DOMAIN)
        self.assertEqual(my_model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)

        REDUCED_DOMAIN=(1,50)
        my_model.domain(*sig_A, *REDUCED_DOMAIN)
        self.assertEqual(len(my_model._domains), 2)
        self.assertEqual(my_model.get_domain_for(*sig_X), REDUCED_DOMAIN)
        self.assertEqual(my_model.get_domain_for(*sig_A), REDUCED_DOMAIN)
        self.assertEqual(my_model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)

        REDUCED_DOMAIN_2=(2,75)
        my_model.domain(*sig_X, *REDUCED_DOMAIN_2)
        self.assertEqual(len(my_model._domains), 2)
        self.assertEqual(my_model.get_domain_for(*sig_X), (2, 50))
        self.assertEqual(my_model.get_domain_for(*sig_A), (2, 50))
        self.assertEqual(my_model.get_domain_for(*sig_B), complexmodel.DEFAULT_DOMAIN)

    def test_export(self):
        my_model = self._model

        my_model.register(self._eq_A, *self._params_A)
        my_model.register(self._eq_B, *self._params_B)
        my_model.bind(self._eq_A, "x", self._eq_B, "a")
        my_model.domain(self._eq_A, "x", 2, 50)

        params, domains, eqs = my_model.export()

        self.assertEqual(len(params), 2)
        self.assertEqual(len(domains), 2)
        self.assertEqual(len(eqs), 2)
        self.assertEqual(len(eqs[0][1]), 1)
        self.assertEqual(len(eqs[1][1]), 2)
        self.assertEqual(eqs[0][1][0], eqs[1][1][0])
        self.assertNotEqual(eqs[1][1][0], eqs[1][1][1])

#        # Take a look at this to understand the above tests:
#        from pprint import pprint
#        pprint(domains)
#        pprint(eqs)
        
class TestComplexModelDomain(unittest.TestCase):
    def test_optional_domain(self):
        """ If the domain is not specified it defaults to DEFAULT_DOMAIN.
        """
        model = complexmodel.ComplexModel()
        fct = lambda x: x
        model.register(
                fct,
                dict(name="x", description="The x parameter"),
                )

        self.assertEqual(model.get_domain_for(fct, "x"), complexmodel.DEFAULT_DOMAIN)

    def test_optional_domain(self):
        """ Each parameter may specify a domain.
        """
        model = complexmodel.ComplexModel()
        fct = lambda x, y, z: x+y+z
        model.register(
                fct,
                dict(name="x", description="The x parameter", domain=(3,4)),
                dict(name="y", description="The y parameter", domain=12),
                dict(name="z", description="The z parameter"),
                )

        self.assertEqual(model.get_domain_for(fct, "x"), (3,4))
        self.assertEqual(model.get_domain_for(fct, "y"), (12,12))
        self.assertEqual(model.get_domain_for(fct, "z"), complexmodel.DEFAULT_DOMAIN)



