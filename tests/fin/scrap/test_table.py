import unittest

from fin.scrap import table

# Private functions
from fin.scrap.table import _union

from bs4 import BeautifulSoup

class TestTableUtils(unittest.TestCase):
    def test_union(self):
        test_cases = (
                "#0 empty",
                [],
                (5, 10),
                [(5, 10)],

                "#1.0 insert before stricly",
                [(5, 10)],
                (1, 3),
                [(1, 3), (5, 10)],

                "#1.1 insert before touch",
                [(5, 10)],
                (1, 5),
                [(1, 10)],

                "#1.2 insert before intersect",
                [(5, 10)],
                (1, 8),
                [(1, 10)],

                "#2.0 insert after stricly",
                [(5, 10)],
                (15, 20),
                [(5, 10), (15, 20)],

                "#2.1 insert after touch",
                [(5, 10)],
                (10, 20),
                [(5, 20)],

                "#2.2 insert after intersect",
                [(5, 10)],
                (8, 20),
                [(5, 20)],

                "#3 insert outside",
                [(5, 10)],
                (1, 20),
                [(1, 20)],

                "#4 insert inside",
                [(5, 10)],
                (7, 9),
                [(5, 10)],

                "#5 join two segments",
                [(5, 10), (15, 20)],
                (10, 15),
                [(5, 20)],

                "#6 intersect two segments",
                [(5, 10), (15, 20)],
                (8, 18),
                [(5, 20)],

                "#7 enclose two segments",
                [(5, 10), (15, 20)],
                (1, 25),
                [(1, 25)],

                "#8 insert between",
                [(5, 10), (20, 25)],
                (15, 17),
                [(5, 10), (15, 17), (20, 25)],

            )

        while test_cases:
            desc, selection, new, expected, *test_cases = test_cases
            with self.subTest(desc=desc):
                actual = _union(selection, *new)
                self.assertSequenceEqual(actual, expected)

class TestTableScraper(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_table_parser(self):
        fname="tests/_fixtures/scrape/table-yf.html"
        expected=\
            [['Market Cap (intraday)', '1.06B'],
             ['Enterprise Value', '1.40B'],
             ['Trailing P/E', '15.29'],
             ['Forward P/E', '12.76'],
             ['PEG Ratio (5 yr expected)', 'N/A'],
             ['Price/Sales(ttm)', '0.60'],
             ['Price/Book(mrq)', '1.34'],
             ['Enterprise Value/Revenue', '0.96'],
             ['Enterprise Value/EBITDA', '6.78']]

        with open(fname, "rt") as f:
            doc = f.read()

        soup = BeautifulSoup(doc, "html.parser")

        tbl = table.parse(soup.table)
        self.assertSequenceEqual(tuple(tbl), expected)

        for idx, (key, value) in enumerate(expected):
            found = tbl.select(key)
            self.assertEqual(found, ((), [(idx, idx+1)]), msg=key)

        for key, value in expected:
            found = tbl.find(key)
            self.assertSequenceEqual(found, [[value]], msg=key)

