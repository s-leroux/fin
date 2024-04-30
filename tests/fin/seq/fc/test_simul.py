import unittest

from fin.seq.fc import simul
from fin.seq.column import Column
from fin.seq.serie import Serie

class CustomAssertions:
    def assertSerieEqual(self, actual, expected, *args, **kwargs):
        self.assertIsInstance(actual, Serie)
        self.assertEqual(actual.headings, expected.headings, *args, **kwargs)
        for n, (a, b) in enumerate(zip(actual.rows, expected.rows)):
            self.assertEqual(a, b, msg=f"First differing row: {n}")

class TestBSS(unittest.TestCase, CustomAssertions):
    def test_basic(self):
        test_cases = (
            "#0 Basic test",
            "inini",
            """\
                T, PRICES, ORDERS, FUNDS, POSITIONS
                0,     10,      0,  1000,         0
                1,     11,      0,  1000,         0
                2,     12,     10,   880,        10
                3,     13,      0,   880,        10
                4,     14,      0,   880,        10
                5,     15,     -5,   955,         5
                6,     16,      0,   955,         5
                7,     17,      0,   955,         5
                8,     18,      3,   901,         8
                9,     19,      0,   901,         8\
            """,
            (
                "T",
                "PRICES",
                "ORDERS",
                (simul.bss(init_funds=1000), "ORDERS", "PRICES"),
            ),

            "#1 Propagate n/a on orders",
            "inini",
            """\
                T, PRICES, ORDERS, FUNDS, POSITIONS
                0,     10,      0,  1000,         0
                1,     11,      0,  1000,         0
                2,     12,     10,   880,        10
                3,     13,    n/a,   n/a,       n/a
                4,     14,      0,   n/a,       n/a
                5,     15,     -5,   n/a,       n/a
                6,    n/a,      0,   n/a,       n/a
                7,     17,    n/a,   n/a,       n/a
                8,     18,      3,   n/a,       n/a
                9,     19,      0,   n/a,       n/a\
            """,
            (
                "T",
                "PRICES",
                "ORDERS",
                (simul.bss(init_funds=1000), "ORDERS", "PRICES"),
            ),

            "#2 Do not propagate n/a on prices without order",
            "inini",
            """\
                T, PRICES, ORDERS, FUNDS, POSITIONS
                0,     10,      0,  1000,         0
                1,     11,      0,  1000,         0
                2,     12,     10,   880,        10
                3,    n/a,      0,   880,        10
                4,     14,      0,   880,        10
                5,     15,     -5,   955,         5
                6,    n/a,      0,   955,         5
                7,     17,      0,   955,         5
                8,     18,      3,   901,         8
                9,     19,      0,   901,         8\
            """,
            (
                "T",
                "PRICES",
                "ORDERS",
                (simul.bss(init_funds=1000), "ORDERS", "PRICES"),
            ),

            "#3 Propagate n/a on prices with order",
            "inini",
            """\
                T, PRICES, ORDERS, FUNDS, POSITIONS
                0,     10,      0,  1000,         0
                1,     11,      0,  1000,         0
                2,     12,     10,   880,        10
                3,    n/a,      0,   880,        10
                4,     14,      0,   880,        10
                5,    n/a,     -5,   n/a,       n/a
                6,     16,      0,   n/a,       n/a
                7,     17,      0,   n/a,       n/a
                8,     18,      3,   n/a,       n/a
                9,     19,      0,   n/a,       n/a\
            """,
            (
                "T",
                "PRICES",
                "ORDERS",
                (simul.bss(init_funds=1000), "ORDERS", "PRICES"),
            ),
        )

        while test_cases:
            desc, fmt, csv, expr, *test_cases = test_cases
            expected = Serie.from_csv(csv, fmt)
            actual = expected.select(*expr)
            with self.subTest(desc=desc):
                self.assertSerieEqual(actual, expected)

