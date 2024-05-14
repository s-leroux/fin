# Floating point data columns are sometimes displayed as ternary values
# https://github.com/s-leroux/fin/issues/45

import unittest

from fin.seq import fc
from fin.seq.column import Column
from fin.seq.serie import Serie

class Test(unittest.TestCase):
    def test(self):
        with open("tests/_fixtures/^FCHI.csv", "rt") as f:
            data = Serie.from_csv(f, "dnnnnn")

        data = data.where(
                (fc.all, "Open", "High", "Low", "Close", "Adj Close"),
            )

        lines = str(data).splitlines()
        last_open = data.columns[1].f_values[-1]

        self.assertEqual(f"{last_open:0.2f}", "7357.68")
