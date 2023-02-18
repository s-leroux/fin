import unittest

import fin.math
import fin.model as model

# ======================================================================
# Exceptions
# ======================================================================
class TestModelExceptions(unittest.TestCase):
    def test_undefined(self):
        with self.assertRaises(fin.model.Underdefined) as cm:
            raise fin.model.Underdefined({'a':None,'b':None,'c':None}, {'a':1})
        self.assertRegex(str(cm.exception),"Too many missing parameters")
        self.assertRegex(str(cm.exception),"'a',\s*'b',\s*'c'")

# ======================================================================
# Model
# ======================================================================
class TestModel(unittest.TestCase):
    def test_raises_undefined(self):
        eq = lambda a, b, c: a + b + c
        params = { 'c': lambda a, b : a + b }
        values = { "a": 1 }

        with self.assertRaises(fin.model.Underdefined):
            m = model.Model(eq, params, values)

    def test_generic_solver(self):
        """
        The generic solver should try to infer missing values
        """
        eq = lambda a, b, c: a + b + c
        params = { 'c': lambda a, b : a + b }
        values = { "a": 1, "c": 3 }

        m = model.Model(eq, params, values)

        self.assertEqual(m["a"], values["a"])
        self.assertEqual(m["c"], values["c"])
        self.assertAlmostEqual(m["b"], -4.00, delta=fin.math.EPSILON)

    def test_custom_solver(self):
        """
        If provided, a custom solver is used to infer missing values
        """
        called = False
        def solve_for_b(a,c):
            nonlocal called
            called = True

            return -a-c

        eq = lambda a, b, c: a + b + c
        params = { 'c': lambda a, b : a + b }
        params["b"] = solve_for_b
        values = { "a": 1, "c": 3 }

        m = model.Model(eq, params, values)

        self.assertEqual(m["a"], values["a"])
        self.assertEqual(m["c"], values["c"])
        self.assertAlmostEqual(m["b"], -4.00, delta=fin.math.EPSILON)
        self.assertTrue(called)

