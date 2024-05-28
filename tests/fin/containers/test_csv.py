import unittest

from fin.containers.csv import CSV

CSV_DATA = """\
Date, Open, High, Low, Close, Adj Close, Volume
2020-01-03, 199.39, 200.55, 198.85, 200.08, 181.49, 2767600
2020-01-06, 199.60, 202.77, 199.35, 202.33, 183.54, 4660400
2020-01-07, 201.87, 202.68, 200.51, 202.63, 183.81, 4047400
2020-01-08, 202.62, 206.69, 202.20, 205.91, 186.78, 5284200
2020-01-09, 206.86, 209.37, 206.10, 208.35, 189.00, 5971600
2020-01-10, 208.44, 208.95, 207.27, 207.27, 188.02, 2336400
2020-01-13, 207.38, 207.78, 205.76, 206.51, 187.33, 2784200
2020-01-14, 205.46, 207.65, 205.46, 207.32, 188.06, 2622700
2020-01-15, 207.32, 210.35, 207.32, 209.77, 190.28, 3369400
"""
HEADINGS = ('Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume')
ROWS = (
    ["2020-01-03", "199.39", "200.55", "198.85", "200.08", "181.49", "2767600"],
    ["2020-01-06", "199.60", "202.77", "199.35", "202.33", "183.54", "4660400"],
    ["2020-01-07", "201.87", "202.68", "200.51", "202.63", "183.81", "4047400"],
    ["2020-01-08", "202.62", "206.69", "202.20", "205.91", "186.78", "5284200"],
    ["2020-01-09", "206.86", "209.37", "206.10", "208.35", "189.00", "5971600"],
    ["2020-01-10", "208.44", "208.95", "207.27", "207.27", "188.02", "2336400"],
    ["2020-01-13", "207.38", "207.78", "205.76", "206.51", "187.33", "2784200"],
    ["2020-01-14", "205.46", "207.65", "205.46", "207.32", "188.06", "2622700"],
    ["2020-01-15", "207.32", "210.35", "207.32", "209.77", "190.28", "3369400"],
)
class TestCSV(unittest.TestCase):
    def test_reader(self):
        csv = CSV.from_text(CSV_DATA, skipinitialspace=True)
        self.assertSequenceEqual(csv.headings, HEADINGS)
        self.assertSequenceEqual(csv.rows, ROWS)

    def test_sequence_interface(self):
        csv = CSV.from_text(CSV_DATA, skipinitialspace=True)
        self.assertSequenceEqual(csv, ROWS)

class TestColumnSelector(unittest.TestCase):
    def test_len(self):
        csv = CSV.from_text(CSV_DATA, skipinitialspace=True)
        self.assertEqual(len(csv.columns), len(HEADINGS))

    def test_select_columns(self):
        test_cases = (
            "#0",
            ("Date", "Open"),
            (0, 1),

            "#1",
            "Volume",
            (-1,)
        )
        while test_cases:
            desc, sel, indices, *test_cases = test_cases
            expected = [ [row[i] for i in indices] for row in ROWS ]

            with self.subTest(desc=desc):
                csv = CSV.from_text(CSV_DATA, skipinitialspace=True)
                self.assertSequenceEqual(csv.columns[sel], expected)
