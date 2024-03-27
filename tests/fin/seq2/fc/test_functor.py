import unittest

from . import functor
from fin.seq2.column import Column
from fin.seq2.serie import Serie
from tests.fin.seq2.fc import utilities

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

        res = fct(serie, self.src1, self.src2)

        self.assertIsInstance(res, Column)
        self.assertSequenceEqual(
                res.py_values,
                [x+y for x,y in zip(self.src1.py_values, self.src2.py_values)]
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
