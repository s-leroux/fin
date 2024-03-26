import unittest

from fin.seq2 import column
from fin.seq2.fc import arithmetics

from tests.fin.seq2.mock import SerieMock

# ======================================================================
# Arithmetic operators
# ======================================================================
class TestArithmeticOperators(unittest.TestCase):
    def call(self, fct, validator, **kwargs):
        serie = SerieMock(**kwargs)

        colA = column.Column.from_sequence(range(10,16))
        colB = column.Column.from_sequence(range(20,26))
        colC = column.Column.from_sequence(range(30,36))

        res = fct(serie, colA, colB, colC)
        
        self.assertIsInstance(res, column.Column)
        self.assertSequenceEqual(res.py_values, [validator(x,y,z) for x,y,z in zip(colA,colB,colC)])

    def test_add(self):
        self.call(arithmetics.add, lambda x,y,z : x+y+z)

    def test_sub(self):
        self.call(arithmetics.sub, lambda x,y,z : x-y-z)

    def test_mul(self):
        self.call(arithmetics.mul, lambda x,y,z : x*y*z)

    def test_div(self):
        self.call(arithmetics.div, lambda x,y,z : x/y/z)

# ======================================================================
# Comparisons
# ======================================================================
class TestComparison(unittest.TestCase):
    def test_min(self):
        rowcount = 100
        n = 8
        serie = SerieMock(rowcount=rowcount)
        
        seq = tuple(range(10,20))*3
        col = column.Column.from_sequence(seq)

        fct = arithmetics.min(n)
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
        serie = SerieMock(rowcount=rowcount)
        
        seq = tuple(range(10,20))*3
        col = column.Column.from_sequence(seq)

        fct = arithmetics.max(n)
        res = fct(serie, col)
        expected = (
                None, None, None, None, None, None, None, 17, 18, 19,
                19, 19, 19, 19, 19, 19, 19, 17, 18, 19,
                19, 19, 19, 19, 19, 19, 19, 17, 18, 19,
                )
        self.assertSequenceEqual(res.py_values, expected)

