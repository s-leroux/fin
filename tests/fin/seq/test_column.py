import unittest
import math
import array

from testing import assertions

from fin.seq import table, column

from fin.seq.column import Column
from fin.seq.column import OldColumn

# ======================================================================
# New column implementation
# ======================================================================
class TestColumn(unittest.TestCase, assertions.ExtraTests):
    def test_create_from_sequence(self):
        """
        You can create a column from a sequence of Python objects.
        """
        seq = [1, 2, 3, None, 5, "abc"]
        c = Column.from_sequence("x", seq)
        self.assertSequenceEqual(c.py_values, seq)

    def test_create_from_float_array(self):
        """
        You can create a column from a float array.
        """
        arr = array.array("d", [1, 2, 3, float("nan"), 5])
        c = Column.from_float_array("x", arr)
        self.assertFloatSequenceEqual(c.f_values, arr)

    def test_sequence_to_float_conversion(self):
        """
        You can access the content of a column as an array of float.
        """
        seq = [1, 2, 3, None, 5]
        arr = array.array("d", [1, 2, 3, float("nan"), 5])
        c = Column.from_sequence("x", seq)
        self.assertFloatSequenceEqual(c.f_values, arr)

    def test_float_to_sequence_conversion(self):
        """
        You can access the content of a column as a sequence of Python objects.
        """
        seq = [1, 2, 3, None, 5]
        arr = array.array("d", [1, 2, 3, float("nan"), 5])
        c = Column.from_float_array("x", arr)
        self.assertSequenceEqual(c.py_values, seq)

    def test_equality(self):
        seq = [1, 2, 3, None, 5]
        c1 = Column.from_sequence("x", seq)
        c2 = Column.from_sequence("x", seq)

        self.assertEqual(c1, c2)

    def test_inequality(self):
        seq = [1, 2, 3, None, 5]
        c1 = Column.from_sequence("x", seq)
        c2 = Column.from_sequence("x", seq + [6])

        self.assertNotEqual(c1, c2)

    def test_len(self):
        """
        You can use `len()` to find the number of items in the column.
        """
        with self.subTest(created="from a float array"):
            arr = array.array("d", [1, 2, 3, float("nan"), 5])
            c = Column.from_float_array("x", arr)

            self.assertEqual(len(c), len(arr))

        with self.subTest(created="from a sequence"):
            seq = [1, 2, 3, None, 5, "abc"]
            c = Column.from_sequence("x", seq)

            self.assertEqual(len(c), len(seq))

    def test_getitem(self):
        """
        You can use the bracket notation to access individual items.
        """
        LEN=10
        cseq = Column.from_sequence("X", range(LEN))
        carr = Column.from_float_array("X", array.array("d", range(LEN)))

        for i in range(LEN):
            with self.subTest(created="from sequence"):
                self.assertEqual(cseq[i], cseq.py_values[i])
            with self.subTest(created="from float array"):
                self.assertEqual(carr[i], carr.f_values[i])

    def test_min_max(self):
        """
        You can find the minimum and maximum values of a column.
        """
        with self.subTest(created="from a float array"):
            arr = array.array("d", [10, 2, 3, float("nan"), 5])
            c = Column.from_float_array("x", arr)

            self.assertEqual(c.min_max(), (2, 10))

        with self.subTest(created="from a sequence"):
            seq = [10, 2, 3, None, 5, float("nan")]
            c = Column.from_sequence("x", seq)

            self.assertEqual(c.min_max(), (2, 10))

    def test_slice(self):
        """
        You can use the slice syntax to copy a part of a column.
        """
        LEN=10
        cseq = Column.from_sequence("X", range(LEN))
        carr = Column.from_float_array("X", array.array("d", range(LEN)))
        use_cases = (
                ( 0, LEN ),
                ( 0, LEN+1 ),
                ( 1, LEN ),
                ( 1, LEN // 2 + 1),
                )

        for use_case in use_cases:
            with self.subTest(use_case=use_case, created="from sequence"):
                start, end = use_case
                self.assertSequenceEqual(cseq[start:end].py_values, cseq.py_values[start:end])
            with self.subTest(use_case=use_case, created="from float array"):
                start, end = use_case
                self.assertSequenceEqual(carr[start:end].f_values, carr.f_values[start:end])

    def test_named(self):
        """
        You can create a copy of a column with a different name.
        """
        LEN=10
        c1 = Column.from_sequence("X", range(LEN))
        c2 = c1.named("Y")

        self.assertEqual(c1.name, "X")
        self.assertEqual(c2.name, "Y")
        self.assertSequenceEqual(c2.py_values, c1.py_values)


# ======================================================================
# Utilities
# ======================================================================
class TestColumnUtilities(unittest.TestCase):
    def test_as_column(self):
        seq = list(range(5))
        testcases = (
            seq,
            Column.from_sequence("x", seq),
                )

        for testcase in testcases:
            c = column.as_column(testcase)
            self.assertIsInstance(c, Column)
            self.assertSequenceEqual(c.py_values, seq)

# ======================================================================
# OldColumns
# ======================================================================
class TestOldColumn(unittest.TestCase):
    def test_eq(self):
        LEN=1
        t1 = table.Table(LEN)
        t1.add_column("A", 1)
        t1.add_column("B", 2)

        t2 = table.Table(LEN)
        t2.add_column("A", 1)
        t2.add_column("B", 1)

        # self equality (aka identity)
        self.assertEqual(t1["A"], t1["A"])
        self.assertEqual(t1["B"], t1["B"])
        self.assertEqual(t2["A"], t2["A"])
        self.assertEqual(t2["B"], t2["B"])

        # (in)equality
        self.assertEqual(t1["A"], t2["A"])
        self.assertNotEqual(t1["A"], t1["B"])
        self.assertEqual(t1["A"], t2["B"]) # The name is ignored for testing equality

    def test_type(self):
        use_cases = (
                ( [1.0]*10, float),
                ( [1.0]*10 + [None], float),
                ( [None] + [1.0]*10 + [None], float),
                )

        for values, expected in use_cases:
            with self.subTest(values=values):
                column = OldColumn("X", values)
                self.assertEqual(column.type(), expected)

