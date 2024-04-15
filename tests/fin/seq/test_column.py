import unittest
import math
import array

from testing import assertions

from fin.seq import column
from fin.seq import coltypes
from fin.seq.column import Column

# ======================================================================
# New column implementation
# ======================================================================
class TestColumnRemap(unittest.TestCase):
    def test_remap_from_py_values(self):
        column = Column.from_sequence("ABCDEF")
        #                                   012345

        actual = column.remap([3,4,0,3,1,4,4,5])

        self.assertSequenceEqual(actual.py_values, "DEADBEEF")

    def test_remap_from_py_values_with_missing(self):
        column = Column.from_sequence("ABCDEF")
        #                                   012345

        actual = column.remap([3,4,0,3,-1,1,4,4,5,-1])

        self.assertSequenceEqual(actual.py_values, tuple((*"DEAD", None, *"BEEF", None)))

    def test_remap_from_f_values(self):
        arr = array.array("d", (10, 20, 30, 40, 50, 60))
        #                        0   1   2   3   4   5
        column = Column.from_float_array(arr)

        actual = column.remap([3,4,0,3,1,4,4,5])

        self.assertSequenceEqual(actual.py_values, (
            40, 50, 10, 40, 20, 50, 50, 60
        ))

def BinOp(name, op, fct):
    class C(unittest.TestCase):
        def test_scalar_op(self):
            scalar = 3
            arr = array.array("d", (10, 20, 30, 40, 50, 60))
            c0 = Column.from_float_array(arr)
            c1 = fct(c0, scalar)

            self.assertSequenceEqual(c1.f_values, [fct(i, scalar) for i in arr])
            self.assertEqual(c1.name, f"({c0.name}{op}{scalar:.1f})")

        def test_column_op(self):
            arr0 = array.array("d", (10, 20, 30, 40, 50, 60))
            arr1 = array.array("d", (11, 21, 31, 41, 51, 61))
            c0 = Column.from_float_array(arr0)
            c1 = Column.from_float_array(arr1)
            c2 = fct(c0, c1)

            self.assertSequenceEqual(c2.f_values, [fct(i, j) for i,j in zip(arr0, arr1)])
            self.assertEqual(c2.name, f"({c0.name}{op}{c1.name})")

    C.__name__ = C.__qualname__ = name
    return C

TestAddition = BinOp("Addition", "+", lambda x,y: x+y)
TestSutraction = BinOp("Subtraction", "+-", lambda x,y: x-y)
TestMultiplication = BinOp("Multiplication", "*", lambda x,y: x*y)
TestDivision = BinOp("Division", "/", lambda x,y: x/y)

class TestColumn(unittest.TestCase, assertions.ExtraTests):
    def test_create_from_sequence(self):
        """
        You can create a column from a constant
        """
        count = 42

        for value in (float(3.14), int(10), str("Hello")):
            c = Column.from_constant(count, value)
            self.assertSequenceEqual(c.py_values, [value]*count)

    def test_create_from_sequence(self):
        """
        You can create a column from a sequence of Python objects.
        """
        seq = [1, 2, 3, None, 5, "abc"]
        c = Column.from_sequence(seq)
        self.assertSequenceEqual(c.py_values, seq)

    def test_create_from_float_array(self):
        """
        You can create a column from a float array.
        """
        arr = array.array("d", [1, 2, 3, float("nan"), 5])
        c = Column.from_float_array(arr)
        self.assertFloatSequenceEqual(c.f_values, arr)

    def test_create_from_callable_1(self):
        """
        You can create a column from a callable and a set of columns.
        """
        def fct(x):
            return x+1

        seq = [1, 2, 3, float("nan"), 5]
        c = Column.from_callable(fct, seq)
        self.assertFloatSequenceEqual(c.py_values, [fct(x) for x in seq])

    def test_create_from_callable_2(self):
        """
        You can create a column from a callable and a set of columns.
        """
        def fct(x, y):
            return 10*x+y

        seq1 = [1, 2, 3, float("nan"), 5]
        seq = [2, 3, float("nan"), 5, 6]
        c = Column.from_callable(fct, seq1, seq)
        self.assertFloatSequenceEqual(c.py_values, [fct(x, y) for x, y in zip(seq1, seq)])

    def test_sequence_to_float_conversion(self):
        """
        You can access the content of a column as an array of float.
        """
        seq = [1, 2, 3, None, 5]
        arr = array.array("d", [1, 2, 3, float("nan"), 5])
        c = Column.from_sequence(seq)
        self.assertFloatSequenceEqual(c.f_values, arr)

    def test_float_to_sequence_conversion(self):
        """
        You can access the content of a column as a sequence of Python objects.
        """
        seq = [1, 2, 3, None, 5]
        arr = array.array("d", [1, 2, 3, float("nan"), 5])
        c = Column.from_float_array(arr)
        self.assertSequenceEqual(c.py_values, seq)

    def test_equality(self):
        seq = [1, 2, 3, None, 5]
        c1 = Column.from_sequence(seq)
        c2 = Column.from_sequence(seq)

        self.assertEqual(c1, c2)

    def test_inequality(self):
        seq = [1, 2, 3, None, 5]
        c1 = Column.from_sequence(seq)
        c2 = Column.from_sequence(seq + [6])

        self.assertNotEqual(c1, c2)

    def test_len(self):
        """
        You can use `len()` to find the number of items in the column.
        """
        with self.subTest(created="from a float array"):
            arr = array.array("d", [1, 2, 3, float("nan"), 5])
            c = Column.from_float_array(arr)

            self.assertEqual(len(c), len(arr))

        with self.subTest(created="from a sequence"):
            seq = [1, 2, 3, None, 5, "abc"]
            c = Column.from_sequence(seq)

            self.assertEqual(len(c), len(seq))

    def test_getitem(self):
        """
        You can use the bracket notation to access individual items.
        """
        LEN=10
        cseq = Column.from_sequence(range(LEN))
        carr = Column.from_float_array(array.array("d", range(LEN)))

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
            c = Column.from_float_array(arr)

            self.assertEqual(c.min_max(), (2, 10))

        with self.subTest(created="from a sequence"):
            seq = [10, 2, 3, None, 5, float("nan")]
            c = Column.from_sequence(seq)

            self.assertEqual(c.min_max(), (2, 10))

    def test_slice(self):
        """
        You can use the slice syntax to copy a part of a column.
        """
        LEN=10
        cseq = Column.from_sequence(range(LEN))
        carr = Column.from_float_array(array.array("d", range(LEN)))
        use_cases = (
                ( 0, LEN ),
#                ( 0, LEN+1 ), # raise an error with fin.containers.Tuple
                ( 1, LEN ),
                ( 1, LEN // 2 + 1),
                )

        for use_case in use_cases:
            with self.subTest(use_case=use_case, created="from sequence"):
                start, end = use_case
                self.assertSequenceEqual(cseq[start:end].py_values, cseq.py_values.tst_slice(start,end))
            with self.subTest(use_case=use_case, created="from float array"):
                start, end = use_case
                self.assertSequenceEqual(carr[start:end].f_values, carr.f_values[start:end])

# ======================================================================
# Column metadata
# ======================================================================
class TestColumnMetadata(unittest.TestCase):
    def test_default_name(self):
        """
        By default a name is infered from the Column's id.
        """
        c = Column.from_sequence([1,2,3])
        self.assertRegex(c.name, ":[0-9]{6}")

    def test_user_name(self):
        """
        You may specify a name at column's creation time.
        """
        c = Column.from_sequence([1,2,3], name="idx")
        self.assertRegex(c.name, "idx")

    def test_default_type(self):
        """
        By default, the type is set to Other.
        """
        c = Column.from_sequence([1,2,3])

        self.assertIsInstance(c.type, coltypes.Other)

    def test_user_type(self):
        """
        You may specify a type at column's creation time.
        """
        class T:
            def from_sequence(self, sequence):
                return tuple(sequence)
        t = T()

        c = Column.from_sequence([1,2,3], type=t)

        self.assertIs(c.type, t)

# ======================================================================
# Mutations
# ======================================================================
class TestMutations(unittest.TestCase):
    def test_shift_positive(self):
        """
        You can shift a column by discarding the initial data.
        """
        col = Column.from_sequence((1,2,3,4,5))
        res = col.shift(2)

        self.assertSequenceEqual(res.py_values, (3,4,5,None,None))

    def test_shift_negative(self):
        """
        You can shift a column by discarding the final data.
        """
        col = Column.from_sequence((1,2,3,4,5))
        res = col.shift(-2)

        self.assertSequenceEqual(res.py_values, (None,None,1,2,3))

    def test_shift_zero(self):
        """
        Shift by zero is the identity operation.
        """
        col = Column.from_sequence((1,2,3,4,5))
        res = col.shift(0)

        self.assertSequenceEqual(res.py_values, (1,2,3,4,5))




# ======================================================================
# Utilities
# ======================================================================
class TestColumnUtilities(unittest.TestCase):
    def test_as_column(self):
        seq = list(range(5))
        testcases = (
            seq,
            Column.from_sequence(seq),
                )

        for testcase in testcases:
            c = column.as_column(testcase)
            self.assertIsInstance(c, Column)
            self.assertSequenceEqual(c.py_values, seq)

