import unittest

from fin.seq2.column import Column
from fin.seq2.fc import projection

from tests.fin.seq2.fc import utilities
from tests.fin.seq2.mock import SerieMock

# ======================================================================
# Projections
# ======================================================================
class TestMap(unittest.TestCase):
    def test_map(self):
        serie = SerieMock()
        seqs = (
            tuple(range(10,16)),
            tuple(range(20,26)),
            tuple(range(30,36)),
        )
        columns = tuple(Column.from_sequence(s) for s in seqs)
        fn = lambda x,y,z : x+y+z

        result = projection.map(fn)(serie, *columns)

        self.assertSequenceEqual(result.py_values, [fn(x,y,z) for x,y,z in zip(*seqs)])

class TestMapChange(unittest.TestCase):
    def test_map_change(self):
        rowcount = 6
        serie = SerieMock(rowcount=rowcount)
        seq = tuple(range(10,10+rowcount))
        column = Column.from_sequence(seq)
        fn = lambda x,y : x-y

        result = projection.map_change(fn)(serie, column)

        self.assertSequenceEqual(result.py_values, (None,1,1,1,1,1,))

