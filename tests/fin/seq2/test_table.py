import unittest

from fin.seq2 import serie
from fin.seq2 import table

class TestTable(unittest.TestCase):
    def test_create_empty_table(self):
        tbl = table.Table()
        self.assertEqual(str(tbl), "")

    def test_create_one_column_table(self):
        tbl = table.Table()
        tbl.append(
            serie.Serie("ABCDEF", (1,2,3,4,5,6))
        )
        
        expected = "\n".join((
                "A, 1",
                "B, 2",
                "C, 3",
                "D, 4",
                "E, 5",
                "F, 6",
        ))
        self.assertEqual(str(tbl), expected)

