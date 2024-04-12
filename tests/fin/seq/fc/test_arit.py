import unittest

from fin.seq.column import Column
from fin.seq.serie import Serie
from fin.seq.fc import arit

# ======================================================================
# Arithmetic operators
# ======================================================================
class TestArithmeticOperators(unittest.TestCase):
    def call(self, fct, validator, **kwargs):
        idx = Column.from_sequence(range(6))
        colA = Column.from_sequence(range(10,16))
        colB = Column.from_sequence(range(20,26))
        colC = Column.from_sequence(range(30,36))
        serie = Serie.create(idx)

        res = fct(serie, colA, colB, colC)
        
        self.assertIsInstance(res, Column)
        self.assertSequenceEqual(res.py_values, [validator(x,y,z) for x,y,z in zip(colA,colB,colC)])

    def test_add(self):
        self.call(arit.add, lambda x,y,z : x+y+z)

    def test_sub(self):
        self.call(arit.sub, lambda x,y,z : x-y-z)

    def test_mul(self):
        self.call(arit.mul, lambda x,y,z : x*y*z)

    def test_div(self):
        self.call(arit.div, lambda x,y,z : x/y/z)

# ======================================================================
# Comparisons
# ======================================================================
class TestComparison(unittest.TestCase):
    def test_min(self):
        rowcount = 100
        n = 8
        seq = tuple(range(10,20))*3
        col = Column.from_sequence(seq)
        idx = Column.from_sequence(range(len(seq)))
        serie = Serie.create(idx)

        fct = arit.min(n)
        res = fct(serie, col)
        expected = (
                None, None, None, None, None, None, None, 10, 11, 12,
                10, 10, 10, 10, 10, 10, 10, 10, 11, 12,
                10, 10, 10, 10, 10, 10, 10, 10, 11, 12,
                )
        self.assertSequenceEqual(res.py_values, expected)

    def test_max(self):
        rowcount = 100
        n = 8
        seq = tuple(range(10,20))*3
        col = Column.from_sequence(seq)
        idx = Column.from_sequence(range(len(seq)))
        serie = Serie.create(idx)

        fct = arit.max(n)
        res = fct(serie, col)
        expected = (
                None, None, None, None, None, None, None, 17, 18, 19,
                19, 19, 19, 19, 19, 19, 19, 17, 18, 19,
                19, 19, 19, 19, 19, 19, 19, 17, 18, 19,
                )
        self.assertSequenceEqual(res.py_values, expected)

