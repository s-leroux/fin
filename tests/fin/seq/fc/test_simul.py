import unittest

from testing import assertions
from fin.seq.fc import simul
from fin.seq.column import Column
from fin.seq.serie import Serie

class TestBSS(unittest.TestCase, assertions.ExtraTests):
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

            "#4 Sell before buy",
            "inini",
            """\
                T, PRICES, ORDERS, FUNDS, POSITIONS
                0,     10,      0,  1000,         0
                1,     11,      0,  1000,         0
                2,     12,    -10,  1000,         0
                3,     13,      0,  1000,         0
                4,     14,      0,  1000,         0
                5,     15,      5,   925,         5
                6,     16,      0,   925,         5
                7,     17,      0,   925,         5
                8,     18,     -3,   979,         2
                9,     19,      0,   979,         2\
            """,
            (
                "T",
                "PRICES",
                "ORDERS",
                (simul.bss(init_funds=1000), "ORDERS", "PRICES"),
            ),

            "#5 With fixed fees",
            "inini",
            """\
                T, PRICES, ORDERS, FUNDS, POSITIONS
                0,     10,      0,  1000,         0
                1,     11,      0,  1000,         0
                2,     12,     10,   879,        10
                3,     13,      0,   879,        10
                4,     14,      0,   879,        10
                5,     15,     -5,   953,         5
                6,     16,      0,   953,         5
                7,     17,      0,   953,         5
                8,     18,      3,   898,         8
                9,     19,      0,   898,         8\
            """,
            (
                "T",
                "PRICES",
                "ORDERS",
                (simul.bss(init_funds=1000, fees=lambda direction, qty, price: 1), "ORDERS", "PRICES"),
            ),

        )

        while test_cases:
            desc, fmt, csv, expr, *test_cases = test_cases
            expected = Serie.from_csv(csv, fmt)
            actual = expected.select(*expr)
            with self.subTest(desc=desc):
                self.assertSerieEqual(actual, expected)

