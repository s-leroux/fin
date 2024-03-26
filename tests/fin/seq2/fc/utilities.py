import unittest

from fin.seq2 import column

from tests.fin.seq2.mock import SerieMock

# ======================================================================
# Test utilities
# ======================================================================
def apply(self, fct, *cols, rowcount=None):
    if rowcount is None:
        rowcount = len(cols[0])

    serie = SerieMock(rowcount=rowcount)
    result = fct(serie, *cols)
    self.assertIsInstance(result, column.Column)

    return result
