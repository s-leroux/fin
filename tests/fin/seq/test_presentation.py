import unittest

from fin.seq.serie import Serie
from fin.seq import presentation
from fin.seq import fc

from tests.fin.seq.utils import ColumnFactory

class TestPresentation(unittest.TestCase):
    def test_presentation(self):
        test_cases = (
                "#0 Serie with one sequence column",
                Serie.create(
                    ColumnFactory.column_from_sequence(*"ABCDEF"),
                    ColumnFactory.column_from_sequence(1,2,3,4,5,6),
                ),
                "\n".join((
                    "A | 1",
                    "B | 2",
                    "C | 3",
                    "D | 4",
                    "E | 5",
                    "F | 6",
                )),

                "#1 Serie with one float column",
                Serie.create(
                    ColumnFactory.column_from_sequence(*"ABCDEF"),
                    ColumnFactory.column_from_float(1,2,3,4,5,6),
                ),
                "\n".join((
                    "A | 1.00",
                    "B | 2.00",
                    "C | 3.00",
                    "D | 4.00",
                    "E | 5.00",
                    "F | 6.00",
                )),

                "#2 Serie with one ternary column",
                Serie.create(
                    ColumnFactory.column_from_sequence(*"ABCDEF"),
                    ColumnFactory.column_from_ternary(True, False, None, None, False, True),
                ),
                "\n".join((
                    "A |  True",
                    "B | False",
                    "C |  None",
                    "D |  None",
                    "E | False",
                    "F |  True",
                )),
            )

        while test_cases:
            desc, ser, expected, *test_cases = test_cases
            with self.subTest(desc=desc):
                pres = presentation.Presentation(
                        heading=False,
                    )
                self.assertEqual(pres(ser), expected)

