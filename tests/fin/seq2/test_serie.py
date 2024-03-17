import unittest

from fin.seq2 import serie
from fin.seq2 import column

class TestSequence(unittest.TestCase):
    def test_create_serie_from_lists(self):
        """
        You can create a serie from lists.
        """
        ser = serie.Serie("ABC", [10, 20, 30])

        self.assertIsInstance(ser.index, column.Column)
        self.assertSequenceEqual(ser.index.py_values, "ABC")

        c0, = ser.columns
        self.assertIsInstance(c0, column.Column)
        self.assertSequenceEqual(c0.py_values, [10, 20, 30])

    def test_add_sequences(self):
        """
        Adding two sequences performs an implicit join.
        """
        serA = serie.Serie("ABCDF", [10, 20, 30, 40, 50])
        serB = serie.Serie("ABCEF", [11, 21, 31, 41, 51])

        serC = serA + serB
        self.assertSequenceEqual(serC.index.py_values, "ABCF")
        self.assertEqual(len(serC.columns), 1)
        self.assertSequenceEqual(serC.columns[0].f_values, (21.0, 41.0, 61.0, 101.0))


class TestJoin(unittest.TestCase):
    def test_index_join(self):
        indexA = tuple("ABCFG")
        indexB = tuple("ABDEFXYZ")
        #               01234

        index, ma, mb = serie.index_join(indexA, indexB)
        self.assertSequenceEqual(ma, [0, 1, 3])
        self.assertSequenceEqual(mb, [0, 1, 4])
        self.assertEqual(index, tuple("ABF"))

    def test_serie_join(self):
        ser0 = serie.Serie("ABCDF", [10, 11, 12, 13, 14])
        ser1 = serie.Serie("ABCEF", [20, 21, 22, 23, 24])

        join = serie.join(ser0, ser1)
        print(join)

        self.assertSequenceEqual(join.index.py_values, "ABCF")

        c0, c1 = join.columns
        self.assertSequenceEqual(c0.py_values, [10, 11, 12, 14])
        self.assertSequenceEqual(c1.py_values, [20, 21, 22, 24])

