import unittest

from fin.seq2 import sequence
from fin.seq2 import column

class TestSequence(unittest.TestCase):
    def test_create_sequence_from_lists(self):
        """
        You can create a sequence from lists.
        """
        seq = sequence.Sequence("ABC", [10, 20, 30])

        self.assertIsInstance(seq.index, column.Column)
        self.assertSequenceEqual(seq.index.py_values, "ABC")

        c0, = seq.columns
        self.assertIsInstance(c0, column.Column)
        self.assertSequenceEqual(c0.py_values, [10, 20, 30])


class TestJoin(unittest.TestCase):
    def test_index_join(self):
        indexA = tuple("ABCFG")
        indexB = tuple("ABDEFXYZ")
        #               01234

        index, ma, mb = sequence.index_join(indexA, indexB)
        self.assertSequenceEqual(ma, [0, 1, 3])
        self.assertSequenceEqual(mb, [0, 1, 4])
        self.assertEqual(index, tuple("ABF"))

    def test_sequence_join(self):
        seq0 = sequence.Sequence("ABCDF", [10, 11, 12, 13, 14])
        seq1 = sequence.Sequence("ABCEF", [20, 21, 22, 23, 24])

        join = sequence.join(seq0, seq1)
        print(join)

        self.assertSequenceEqual(join.index.py_values, "ABCF")

        c0, c1 = join.columns
        self.assertSequenceEqual(c0.py_values, [10, 11, 12, 14])
        self.assertSequenceEqual(c1.py_values, [20, 21, 22, 24])

