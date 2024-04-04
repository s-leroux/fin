import unittest

from fin.seq.fc import windows

from tests.fin.seq.fc import utilities

# ======================================================================
# Window functions
# ======================================================================
class TestWindow(unittest.TestCase):
    def test_one_column(self):
        col = utilities.apply(self,
            windows.naive_window(sum, 2),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(col.py_values, [ None, 21, 23, 25, 27, 29, 31, 33, 35, 37 ])
