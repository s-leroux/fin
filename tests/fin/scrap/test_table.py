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

    def test_table_parser_1D(self):
        test_cases = (
                "tests/_fixtures/scrape/table-yf.html",
                [['Market Cap (intraday)', '1.06B'],
                 ['Enterprise Value', '1.40B'],
                 ['Trailing P/E', '15.29'],
                 ['Forward P/E', '12.76'],
                 ['PEG Ratio (5 yr expected)', 'N/A'],
                 ['Price/Sales(ttm)', '0.60'],
                 ['Price/Book(mrq)', '1.34'],
                 ['Enterprise Value/Revenue', '0.96'],
                 ['Enterprise Value/EBITDA', '6.78']],
            )

        while test_cases:
            fname, expected, *test_cases = test_cases

            with open(fname, "rt") as f:
                doc = f.read()

            soup = BeautifulSoup(doc, "html.parser")

            tbl = table.parse(soup.table)
            self.assertSequenceEqual(tuple(tbl), expected)

            with self.subTest(desc=fname):
                for idx, (key, value) in enumerate(expected):
                    found = tbl.select(key)
                    self.assertEqual(found, ((), [(idx, idx+1)]), msg=key)

                for key, value in expected:
                    found = tbl.find(key)
                    self.assertSequenceEqual(found, [[value]], msg=key)


    def test_table_parser_2D(self):
        fname = "tests/_fixtures/scrape/table-marketscreener.html"
        expected = (['Fiscal Period: December',
          '2019',
          '2020',
          '2021',
          '2022',
          '2023',
          '2024',
          '2025',
          '2026'],
         ['Net sales',
          '1,336',
          '1,344',
          '1,227',
          '1,508',
          '1,465',
          '1,203',
          '1,389',
          '1,487'],
         ['EBITDA',
          '157.8',
          '14.51',
          '181.6',
          '229.2',
          '262.4',
          '151.5',
          '195.6',
          '205.2'],
         ['EBIT', '82', '-86.56', '95.8', '154.7', '206.8', '98.43', '136.8', '149.2'],
         ['Operating\n          Margin',
          '6.14%',
          '-6.44%',
          '7.81%',
          '10.26%',
          '14.11%',
          '8.18%',
          '9.84%',
          '10.04%'],
         ['Earnings before Tax (EBT)',
          '71',
          '-',
          '98.4',
          '142.7',
          '239.1',
          '101.9',
          '-',
          '-'],
         ['Net income',
          '49.5',
          '-80.88',
          '73.4',
          '103.1',
          '185',
          '84.77',
          '113.4',
          '128.2'],
         ['Net margin',
          '3.7%',
          '-6.02%',
          '5.98%',
          '6.84%',
          '12.63%',
          '7.05%',
          '8.16%',
          '8.63%'],
         ['EPS', '0.6000', '-', '0.8900', '1.250', '2.230', '1.024', '1.362', '1.580'],
         ['Free Cash Flow',
          '-6.5',
          '108.6',
          '176.3',
          '28.3',
          '82',
          '87.87',
          '96.37',
          '122.6'],
         ['FCF margin',
          '-0.49%',
          '8.08%',
          '14.37%',
          '1.88%',
          '5.6%',
          '7.3%',
          '6.94%',
          '8.24%'],
         ['FCF Conversion\n          (EBITDA)',
          '-',
          '748.54%',
          '97.08%',
          '12.35%',
          '31.25%',
          '58%',
          '49.27%',
          '59.72%'],
         ['FCF Conversion (Net\n          income)',
          '-',
          '-',
          '240.19%',
          '27.45%',
          '44.33%',
          '103.66%',
          '84.98%',
          '95.56%'],
         ['Dividend per Share',
          '0.2300',
          '-',
          '0.3000',
          '0.4200',
          '0.7300',
          '0.3925',
          '0.4633',
          '0.5100'],
         ['Announcement Date',
          '10/29/19',
          '4/30/21',
          '3/17/22',
          '3/22/23',
          '3/19/24',
          '-',
          '-',
          '-'])

        with open(fname, "rt") as f:
            doc = f.read()

        soup = BeautifulSoup(doc, "html.parser")

        tbl = table.parse(soup.table)
        self.assertSequenceEqual(tuple(tbl), expected)

        with self.subTest(desc="Row query"):
            ebitda = tbl.find("EBITDA")
            self.assertSequenceEqual(ebitda, [tbl.data[2][1:]])

        with self.subTest(desc="Col query"):
            ebitda = tbl.find("2020")
            self.assertSequenceEqual(ebitda, [[row[2]] for row in tbl.data[1:]])

        with self.subTest(desc="Cell query"):
            ebitda = tbl.find("2020", "EBITDA")
            self.assertSequenceEqual(ebitda, [[tbl.data[2][2]]])

