import unittest

from fin.seq.column import Column
from fin.seq.serie import Serie
from fin.seq.fc import comp

# ======================================================================
# Arithmetic operators
# ======================================================================
class TestComp(unittest.TestCase):
    def test_comp(self):
        TR = True
        FA = False

        test_data = (
                # R0  R1  R2  R3  R4  R5
                ( 50, 50, 50, 50, 50, 50, ), # C0
                ( 50, 51, 51, 49, 49, 49, ), # C1
                ( 50, 52, 52, 48, 48, 48, ), # C2
                ( 50, 53, 52, 47, 48, 49, ), # C3
                ( 50, 54, 54, 46, 46, 46, ), # C4
                ( 50, 55, 55, 45, 45, 45, ), # C5
            )
        test_cases = (
                "#1 Lower than",
                comp.lt,
                ( FA, TR, FA, FA, FA, FA, ),
                "#1 Greater than",
                comp.gt,
                ( FA, FA, FA, TR, FA, FA, ),
            )

        while test_cases:
            desc, fct, expected, *test_cases = test_cases
            cols = [ Column.from_sequence(col, name=n) for col,n in zip(test_data, "ABCDEF") ]
            serie = Serie.create(
                    Column.from_sequence(range(6), name="T"),
                    *cols,
                )

            with self.subTest(desc=desc):
                actual = fct(serie, *cols)
                self.assertSequenceEqual(tuple(actual),  expected)
