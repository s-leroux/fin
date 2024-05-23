import unittest

from fin.scrap import table

from bs4 import BeautifulSoup

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

            res = table.parse(soup.table)
            self.assertSequenceEqual(res, expected)
