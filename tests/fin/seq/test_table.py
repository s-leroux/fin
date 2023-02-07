import unittest

from fin.seq import table
from fin.seq import column

class TestTable(unittest.TestCase):
    def test_constructor(self):
        t = table.Table()

        self.assertEqual(t.rows(), 0)
        self.assertEqual(t.columns(), 0)

    def test_one_col(self):
        t = table.Table()

        t.append(column.range(1,100))

        self.assertEqual(t.rows(), 99)
        self.assertEqual(t.columns(), 1)

class TestColumnRef(unittest.TestCase):
    def test_add(self):
        FROM = 1
        TO = 101
        N = 2
        t = table.Table()

        t.append(column.range(FROM, TO))
        col = t.get_column(0)

        self.assertEqual(col+N, list(range(FROM+N, TO+N)))

class TestCSV(unittest.TestCase):
    def test_load(self):
        t = table.table_from_csv("tests/_fixtures/bd.csv", format="dn-n")

        self.assertEqual(t.rows(), 284)
        self.assertEqual(t.columns(), 3)

        time = t.get_column("time")
        self.assertEqual(time[0], "2022-01-03")
        self.assertEqual(time[-1], "2023-02-07")

        quote = t.get_column("BOURSE DIRECT")
        self.assertEqual(quote[0], 2.73)
        self.assertEqual(quote[-1], 3.49)

