import unittest

from . import functor
from fin.seq.column import Column
from fin.seq.serie import Serie
from tests.fin.seq.fc import utilities

# ======================================================================
# Functors
# ======================================================================
class TestFunctor(unittest.TestCase):
    def setUp(self):
        self.idx = Column.from_sequence("ABCDEF")
        self.src1 = Column.from_sequence(range(10,16))
        self.src2 = Column.from_sequence(range(20,26))
        self.src3 = Column.from_sequence(range(30,36))

    def test_functor_1(self):
        fct = functor.Functor1Example()
        serie = Serie.create(self.idx)

        res = fct(serie, self.src1)

        self.assertIsInstance(res, Column)
        self.assertSequenceEqual(res.py_values, self.src1.py_values)

    def test_functor_2(self):
        fct = functor.Functor2Example()
        serie = Serie.create(self.idx)

        res = fct(serie, self.src2, self.src3)

        self.assertIsInstance(res, Column)
        self.assertSequenceEqual(
                res.py_values,
                [x+y for x,y in zip(self.src2.py_values, self.src3.py_values)]
        )

    def test_functor_3(self):
        fct = functor.Functor3Example()
        serie = Serie.create(self.idx)

        res = fct(serie, self.src1, self.src2, self.src3)

        self.assertIsInstance(res, Column)
        self.assertSequenceEqual(
                res.py_values,
                [x+y+z for x,y,z in zip(self.src1.py_values, self.src2.py_values, self.src3.py_values)]
        )

    def test_functor_1_3(self):
        fct = functor.Functor1_3Example()
        serie = Serie.create(self.idx)

        res = fct(serie, self.src1)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 3)
        self.assertSequenceEqual(
                res[0],
                self.src1
        )

    def test_functor_2_3(self):
        fct = functor.Functor2_3Example()
        serie = Serie.create(self.idx)

        res = fct(serie, self.src1, self.src2)

        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 3)
        self.assertSequenceEqual(
                res[0],
                [x+y for x,y in zip(self.src1.py_values, self.src2.py_values)]
        )

    def test_functor_N(self):
        fct = functor.FunctorN_Example()
        serie = Serie.create(self.idx)

        res = fct(serie, self.src1, self.src1, self.src2, self.src2)

        self.assertIsInstance(res, Column)
        self.assertSequenceEqual(
                res,
                [x+x+y+y for x,y in zip(self.src1.py_values, self.src2.py_values)]
        )

