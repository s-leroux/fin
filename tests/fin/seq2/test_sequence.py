import unittest

from fin.seq2 import sequence

class TestJoin(unittest.TestCase):
    def test_index_join(self):
        indexA = tuple("ABCFG")
        indexB = tuple("ABDEF")
        #               01234

        ma, mb = sequence.index_join(indexA, indexB)
        self.assertSequenceEqual(ma, [0, 1, 3])
        self.assertSequenceEqual(mb, [0, 1, 4])
