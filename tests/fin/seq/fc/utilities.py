import unittest

from fin.seq.column import Column
from fin.seq.serie import Serie

# ======================================================================
# Test utilities
# ======================================================================
def apply(self, fct, *cols, rowcount=None):
    if rowcount is None:
        rowcount = len(cols[0])

    cols = [col if col is Column else Column.from_sequence(col) for col in cols]

    serie = Serie.create(Column.from_sequence(range(rowcount)))
    result = fct(serie, *cols)
    self.assertIsInstance(result, Column)

    return result
