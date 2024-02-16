import unittest
from testing.assertions import ExtraTests

import random
from fin.seq import algo

from fin.seq import column
ROUNDING=8
def eval(self, fct, *cols):
    try:
        nrows = len(cols[0])
    except IndexError:
        # Fallback in case we want to test zero-column expressions.
        nrows = 10

    result = fct(nrows, *cols)
    self.assertIsInstance(result, column.Column)

    return [round(x, ROUNDING) if type(x) is float else x for x in result]

class TestWindow(unittest.TestCase):
    def test_one_column(self):
        actual = eval(self,
            algo.naive_window(sum, 2),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [ None, 21, 23, 25, 27, 29, 31, 33, 35, 37 ])

class TestByRow(unittest.TestCase, ExtraTests):
    def test_by_row(self):
        LEN=10
        A=list(range(100,100+LEN))
        B=list(range(200,200+LEN))
        cols = [ A, B ]

        fct = algo.by_row(lambda a,b: a+b)
        actual = fct(LEN, A, B)

        self.assertIterableEqual(actual, list(range(300, 300+2*LEN, 2)))

class Test_Sum(unittest.TestCase):
    def test__sum(self):
        from fin.seq.algox import _Sum
        actual = eval(self,
            _Sum(4),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [None, None, None, 46.0, 50.0, 54.0, 58.0, 62.0, 66.0, 70.0])

class TestMul(unittest.TestCase):
    def test_mul(self):
        actual = eval(self,
            algo.mul(),
            [*range(0,10)],
            [*range(10,20)],
            [*range(100,110)],
        )

        self.assertSequenceEqual(actual, [
            0.0,
            1111.0,
            2448.0,
            4017.0,
            5824.0,
            7875.0,
            10176.0,
            12733.0,
            15552.0,
            18639.0,
        ])

    def test_mul_one_columns(self):
        lst = [*range(0,10)]
        actual = eval(self,
            algo.mul(),
            lst,
        )
        self.assertSequenceEqual(actual, lst)

    def test_mul_zero_columns(self):
        actual = eval(self,
            algo.mul(),
        )
        self.assertSequenceEqual(actual, [1.0]*10)


class TestDiv(unittest.TestCase):
    def test_div(self):
        a = [*range(0,10)]
        b = [*range(10,20)]
        c = [*range(100,110)]
        actual = eval(self,
            algo.div(),
            [x*y*z for x,y,z in zip(a,b,c)],
            b,
            c,
        )

        self.assertSequenceEqual(actual, a);

    def test_div_one_columns(self):
        lst = [*range(0,10)]
        actual = eval(self,
            algo.div(),
            lst,
        )
        self.assertSequenceEqual(actual, [float("inf"), *(round(1/x,8) for x in lst[1:])])

    def test_div_zero_columns(self):
        actual = eval(self,
            algo.div(),
        )
        self.assertSequenceEqual(actual, [None]*10)

class TestSub(unittest.TestCase):
    def test_sub(self):
        actual = eval(self,
            algo.sub(),
            [*range(100,110)],
            [*range(10,20)],
            [*range(0,10)],
        )

        self.assertSequenceEqual(actual, [90.0, 89.0, 88.0, 87.0, 86.0, 85.0, 84.0, 83.0, 82.0, 81.0])

    def test_sub_one_columns(self):
        lst = [*range(0,10)]
        actual = eval(self,
            algo.sub(),
            lst,
        )
        self.assertSequenceEqual(actual, [-x for x in lst])


    def test_sub_zero_columns(self):
        actual = eval(self,
            algo.sub(),
        )
        self.assertSequenceEqual(actual, [0.0]*10)


class TestSub(unittest.TestCase):
    def test_sub(self):
        actual = eval(self,
            algo.sub(),
            [*range(100,110)],
            [*range(10,20)],
            [*range(0,10)],
        )

        self.assertSequenceEqual(actual, [90.0, 89.0, 88.0, 87.0, 86.0, 85.0, 84.0, 83.0, 82.0, 81.0])

    def test_sub_one_columns(self):
        lst = [*range(0,10)]
        actual = eval(self,
            algo.sub(),
            lst,
        )
        self.assertSequenceEqual(actual, [-x for x in lst])


    def test_sub_zero_columns(self):
        actual = eval(self,
            algo.sub(),
        )
        self.assertSequenceEqual(actual, [0.0]*10)

class TestSimpleMovingAverage(unittest.TestCase):
    def test_sma(self):
        actual = eval(self,
            algo.sma(2),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [ None, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5 ])


class TestIndicators(unittest.TestCase):
    """
    Test engine for indicators.
    """
    def test_indicators(self):
        #
        # Test definitions
        #
        tests = [
            #
            # Average True Range
            #
            [
                algo.atr(4),
                "from 'Technical Analysis from A to Z, 2nd edition', p69",
                3, 1, # data geometry
                4, # precision
                # Data
                # tesseract --psm 6 photo.png - | sed -E -e 's/\s12\.?/ 12./g' -e 's/\s-?0/&./g' -e 's/\.\././g' | column -t
                12.3125, 12.1875, 12.2500, None,
                12.2500, 12.1562, 12.1875, None,
                12.3125, 12.1875, 12.2500, None,
                12.2812, 12.1250, 12.1875, 0.1250,
                12.3750, 12.1250, 12.3750, 0.1562,
                12.3750, 12.2812, 12.3125, 0.1406,
                12.3125, 12.1875, 12.2188, 0.1367,
                12.3750, 12.1875, 12.3438, 0.1494,
                12.5000, 12.2812, 12.5000, 0.1668,
                12.5938, 12.3125, 12.3750, 0.1954,
                12.3438, 12.2812, 12.3438, 0.1700,
                12.4062, 12.2812, 12.3438, 0.1587,
                12.3750, 12.2812, 12.2812, 0.1425,
                12.4062, 12.2812, 12.3750, 0.1381,
                12.3750, 11.9688, 12.0938, 0.2052,
                12.2812, 12.0938, 12.1562, 0.2007,
                12.2500, 12.0000, 12.0625, 0.2130,
                12.0625, 11.6562, 11.9688, 0.2614,
                12.3125, 12.1562, 12.1875, 0.2819,
                12.3125, 12.1250, 12.1562, 0.2583,
            ],
            [
                algo.atr(5),
                "from https://github.com/TulipCharts/tulipindicators/blob/master/tests/untest.txt",
                3, 1, # data geometr
                3, # precision
                # Data
                82.15,  81.29,  81.59,  None,
                81.89,  80.64,  81.06,  None,
                83.03,  81.31,  82.87,  None,
                83.3,   82.65,  83.0,   None,
                83.85,  83.07,  83.61,  1.116,
                83.9,   83.11,  83.15,  1.051,
                83.33,  82.49,  82.84,  1.009,
                84.3,   82.3,   83.99,  1.207,
                84.84,  84.15,  84.55,  1.136,
                85.0,   84.11,  84.36,  1.086,
                85.9,   84.03,  85.53,  1.243,
                86.58,  85.39,  86.54,  1.233,
                86.98,  85.76,  86.89,  1.23,
                88.0,   87.17,  87.77,  1.206,
                87.87,  87.01,  87.29,  1.137,
            ],
            #
            # Exponential Moving Average
            #
            [
                algo.ema(3),
                "ema",
                1, 1, # data geometry
                5, # precision
                # Data
                10, None,
                11, None,
                12, None,
                13, 12.12500, # XXX should we discard that value or not?
                14, 13.06250,
                15, 14.03125,
                16, 15.01562,
                17, 16.00781,
                18, 17.00391,
                19, 18.00195,
            ],
            #
            # Exponential Moving Average
            #
            [
                algo.ema(3),
                "ema with missing data",
                1, 1, # data geometry
                5, # precision
                # Data
                10,   None,
                11,   None,
                12,   None,
                13,   12.12500,
                14,   13.06250,
                None, None,
                16,   None,
                17,   None,
                18,   None,
                19,   18.12500,
            ],
            #
            # True Range
            #
            [
                algo.tr,
                "from 'Technical Analysis from A to Z, 2nd edition', p69",
                3, 1, # data geometry
                4, # precision
                # Data
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2500, 12.1562, 12.1875, 0.0938,
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2812, 12.1250, 12.1875, 0.1562,
                12.3750, 12.1250, 12.3750, 0.2500,
                12.3750, 12.2812, 12.3125, 0.0938,
                12.3125, 12.1875, 12.2188, 0.1250,
                12.3750, 12.1875, 12.3438, 0.1875,
                12.5000, 12.2812, 12.5000, 0.2188,
                12.5938, 12.3125, 12.3750, 0.2813,
                12.3438, 12.2812, 12.3438, 0.0938,
                12.4062, 12.2812, 12.3438, 0.1250,
                12.3750, 12.2812, 12.2812, 0.0938,
                12.4062, 12.2812, 12.3750, 0.1250,
                12.3750, 11.9688, 12.0938, 0.4062,
                12.2812, 12.0938, 12.1562, 0.1874,
                12.2500, 12.0000, 12.0625, 0.2500,
                12.0625, 11.6562, 11.9688, 0.4063,
                12.3125, 12.1562, 12.1875, 0.3437,
                12.3125, 12.1250, 12.1562, 0.1875,
            ],
            [
                algo.tr,
                "tr with missing data",
                3, 1, # data geometry
                4, # precision
                # Data
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2500, 12.1562, 12.1875, 0.0938,
                12.3125, 12.1875, 12.2500, 0.1250,
                12.2812, 12.1250, 12.1875, 0.1562,
                12.3750, 12.1250, 12.3750, 0.2500,
                12.3750, 12.2812, 12.3125, 0.0938,
                12.3125,    None, 12.2188,   None,
                12.3750, 12.1875, 12.3438, 0.1875,
                12.5000, 12.2812, 12.5000, 0.2188,
                12.5938, 12.3125, 12.3750, 0.2813,
                12.3438, 12.2812, 12.3438, 0.0938,
                12.4062, 12.2812,    None, 0.1250,
                12.3750, 12.2812, 12.2812, 0.0938,
                12.4062, 12.2812, 12.3750, 0.1250,
                12.3750, 11.9688, 12.0938, 0.4062,
                   None, 12.0938, 12.1562,   None,
                12.2500, 12.0000, 12.0625, 0.2500,
                12.0625, 11.6562, 11.9688, 0.4063,
                12.3125, 12.1562, 12.1875, 0.3437,
                12.3125, 12.1250, 12.1562, 0.1875,
            ],
            #
            # Wilder's Smooting
            #
            [
                algo.wilders(5),
                "from 'Technical Analysis from A to Z, 2nd edition', p366",
                1, 1, # data geometry
                4, # precision
                # Data
                62.1250, None,
                61.1250, None,
                62.3438, None,
                65.3125, None,
                63.9688, 62.9750,
                63.4375, 63.0675,
                63.0000, 63.0540,
                63.7812, 63.1995,
                63.4062, 63.2408,
                63.4062, 63.2739,
                62.4375, 63.1066,
                61.8438, 62.8540,
            ],
            [
                algo.wilders(5),
                "from https://github.com/TulipCharts/tulipindicators/blob/master/tests/untest.txt",
                1, 1, # data geometry
                3, # precision
                # Data
                81.59, None,
                81.06, None,
                82.87, None,
                83.00, None,
                83.61, 82.426,
                83.15, 82.571,
                82.84, 82.625,
                83.99, 82.898,
                84.55, 83.228,
                84.36, 83.455,
                85.53, 83.870,
                86.54, 84.404,
                86.89, 84.901,
                87.77, 85.475,
                87.29, 85.838,
            ],
            [
                algo.wilders(5),
                "wilders with missing data",
                1, 1, # data geometry
                3, # precision
                # Data
                81.59, None,
                81.06, None,
                82.87, None,
                83.00, None,
                83.61, 82.426,
                83.15, 82.571,
                82.84, 82.625,
                None,  None,
                84.55, None,
                84.36, None,
                85.53, None,
                86.54, None,
                86.89, 85.574,
                87.77, 86.013,
                87.29, 86.269,
            ],
        ]
        #
        # End of definitions
        #

        for (fct, desc, input_size, output_size, precision, *data) in tests:
            # Split the data in columns
            total_size = input_size+output_size
            src = []
            for i in range(input_size):
                src.append(data[i::total_size])
            expected = []
            for i in range(input_size, total_size):
                expected.append(data[i::total_size])

            try:
                nrows = len(src[0])
            except IndexError:
                # Fallback in case we want to test zero-column expressions.
                nrows = 10

            with self.subTest(fct=fct, desc=desc):
                actual = [ fct(nrows, *src) ]
                actual = [[x and round(x, precision) for x in col] for col in actual]
                self.assertSequenceEqual(actual, expected)

class TestStandardDeviation(unittest.TestCase):
    def test_standard_deviation(self):
        actual = eval(self,
            algo.standard_deviation(3),
            [x**2 for x in range(10, 20)],
        )

        self.assertSequenceEqual(actual, [
            None,
            None,
            22.00757445,
            24.00694344,
            26.00640947,
            28.00595175,
            30.00555504,
            32.00520791,
            34.00490161,
            36.00462933,
        ])

    def test_variance(self):
        actual = eval(self,
            algo.variance(5),
            [x**2 for x in range(10, 20)],
        )

        self.assertSequenceEqual(actual, [
            None,
            None,
            None,
            None,
            1443.5,
            1693.5,
            1963.5,
            2253.5,
            2563.5,
            2893.5,
        ])

    def test_propagate_nones(self):
        data = [x**2 for x in range(10, 20)]
        data[5] = None
        data[6] = None

        actual = eval(self,
            algo.standard_deviation(3),
            data,
        )

        self.assertSequenceEqual(actual, [
            None,
            None,
            22.00757445,
            24.00694344,
            26.00640947,
            None,
            None,
            None,
            None,
            36.00462933,
        ])

class TestCorrelation(unittest.TestCase):
    def test_correlation_with_itself(self):
        """
        The correlation of a column against itself is 1.0.
        """
        EXPECTED = [None]*5 + [1.0]
        LEN = len(EXPECTED)
        INPUT = random.sample([*range(LEN)], LEN)
        actual = eval(self,
            algo.correlation(LEN),
            INPUT,
            INPUT
        )

        self.assertSequenceEqual(actual, EXPECTED)

    def test_correlation(self):
        """
        The correlation of a column against itself is 1.0.
        """
        X = [ 4.0, 2.0, 3.0, 1.0 ]
        Y = [x*-10 for x in X]
        EXPECTED = [None, -1.0, -1.0, -1.0]
        actual = eval(self,
            algo.correlation(2),
            X,
            Y
        )

        self.assertSequenceEqual(actual, EXPECTED)

class TestVolatility(unittest.TestCase):
    def test_volatility(self):
        # Data from John C. Hull "Options, Futures, and Other Devicatives, 5th ed." p240
        INPUT=[
            20.00,
            20.10,
            19.90,
            20.00,
            20.50,
            20.25,
            20.90,
            20.90,
            20.90,
            20.75,
            20.75,
            21.00,
            21.10,
            20.90,
            20.90,
            21.25,
            21.40,
            21.40,
            21.25,
            21.75,
            22.00,
        ]
        WINDOW=len(INPUT)-1
        OUTPUT = [*[None]*WINDOW, 0.19302342]

        actual = eval(self, algo.volatility(WINDOW), INPUT)

        self.assertSequenceEqual(actual, OUTPUT)

class TestBestFit(unittest.TestCase):
    def test_best_fit(self):
        actual = eval(self,
                algo.best_fit,
                [*range(5)],
                [
                    1,
                    4,
                    4,
                    4,
                    7,
                ]
        )

        self.assertSequenceEqual(actual, [
            1.6,
            2.8,
            4.0,
            5.2,
            6.4,
        ])

class TestBeta(unittest.TestCase):
    def test_beta(self):
        LEN = 100
        WINDOW = 10
        COL_X = COL_Y = [*range(LEN)]
        EXPECTED = [None]*(WINDOW-1) + [1.0]*(LEN-WINDOW+1)

        actual = eval(self, algo.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual, EXPECTED)

    def test_beta_x10(self):
        LEN = 100
        WINDOW = 10
        COL_X = [*range(LEN)]
        COL_Y = [x*10 for x in COL_X]
        EXPECTED = [None]*(WINDOW-1) + [10.0]*(LEN-WINDOW+1)

        actual = eval(self, algo.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual, EXPECTED)

    def test_beta_neg(self):
        LEN = 100
        WINDOW = 10
        COL_X = [*range(LEN)]
        COL_Y = [-x for x in COL_X]
        EXPECTED = [None]*(WINDOW-1) + [-1.0]*(LEN-WINDOW+1)

        actual = eval(self, algo.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual, EXPECTED)

class TestMapChange(unittest.TestCase):
    def test_map_change(self):
        INPUT=list(range(1,10))
        OUTPUT = [None, *range(3, 19, 2)]

        actual = eval(self, algo.map_change(lambda a,b: a+b), INPUT)

        self.assertSequenceEqual(actual, OUTPUT)

class TestMapN(unittest.TestCase):
    def test_map_n_0(self):
        LEN=10
        A = list(range(0, LEN))
        B = list(range(1, LEN+1))
        F=lambda a,b: a+b
        EXPECTED = list(range(1, 2*LEN+1, 2))
        actual = eval(self, algo.mapn(F), A, B)

        self.assertSequenceEqual(actual, EXPECTED)

class TestLine(unittest.TestCase):
    def test_line(self):
        LEN = 10
        X = [*range(LEN)]
        Y = [x*10.0 for x in X]
        EXPECTED=Y.copy()
        for a in range(LEN):
            for b in range(LEN):
                if a != b:
                    with self.subTest(locals=locals()):
                        actual = eval(self, algo.line(a,b), X, Y)
                        self.assertSequenceEqual(actual, EXPECTED)

# ======================================================================
# Core functions
# ======================================================================
class TestShift(unittest.TestCase):
    def setUp(self):
        LEN = self.LEN = 10
        self._list = list(range(0, LEN))

    def test_shift_neg(self):
        DELTA=3
        EXPECTED = [None]*DELTA + self._list[:-DELTA]
        actual = eval(self, algo.shift(-DELTA), self._list)

        self.assertSequenceEqual(actual, EXPECTED)

    def test_shift_pos(self):
        DELTA=3
        EXPECTED = self._list[DELTA:] + [None]*DELTA
        actual = eval(self, algo.shift(DELTA), self._list)

        self.assertSequenceEqual(actual, EXPECTED)

class TestMax(unittest.TestCase):
    def test_max(self):
        l = [1, 3, 3, 2, 4, 5, 3, 1, 1, 1, 1]
        expected = [None, None, 3, 3, 4, 5, 5, 5, 3, 1, 1]
        actual = eval(self, algo.max(3), l)

        self.assertSequenceEqual(actual, expected)

    def test_max_none(self):
        l = [1, 3, 3, 2, 4, 5, None, 1, 1, 1, 1]
        expected = [None, None, 3, 3, 4, 5, None, None, None, 1, 1]
        actual = eval(self, algo.max(3), l)

        self.assertSequenceEqual(actual, expected)

class TestMin(unittest.TestCase):
    def test_min(self):
        l = [1, 3, 3, 2, 4, 5, 3, 1, 1, 1, 1]
        expected = [None, None, 1, 2, 2, 2, 3, 1, 1, 1, 1]
        actual = eval(self, algo.min(3), l)

        self.assertSequenceEqual(actual, expected)

    def test_min(self):
        l = [1, 3, 3, 2, 4, 5, None, 1, 1, 1, 1]
        expected = [None, None, 1, 2, 2, 2, None, None, None, 1, 1]
        actual = eval(self, algo.min(3), l)

        self.assertSequenceEqual(actual, expected)

class TestRatio(unittest.TestCase):
    def test_ratio(self):
        L=10
        colA = list(range(-L, L+1))
        colB = list(range(1,2*L+2))

        expected = [round(a_i/b_i, ROUNDING) for a_i, b_i in zip(colA, colB)]
        actual = eval(self, algo.ratio, colA, colB)

        self.assertSequenceEqual(actual, expected)

    def test_ratio_inf_undef(self):
        L=10
        colA = list(range(-L, L+1))
        colB = [0.0]*(2*L+1)

        expected = [float("-inf")]*L + [None] + [float("inf")]*L
        actual = eval(self, algo.ratio, colA, colB)

        self.assertSequenceEqual(actual, expected)

class TestDelta(unittest.TestCase):
    def test_delta(self):
        LEN=10
        col = [*range(LEN)]

        expected = [None] + [1]*(LEN-1)
        actual = eval(self, algo.delta(), col)

        self.assertSequenceEqual(actual, expected)

    def test_delta_with_none(self):
        LEN=10
        IDX=5
        col = [*range(LEN)]
        col[IDX] = None

        expected = [None] + [1]*(LEN-1)
        expected[IDX] = None
        expected[IDX+1] = None
        actual = eval(self, algo.delta(), col)

        self.assertSequenceEqual(actual, expected)

class TestMap(unittest.TestCase):
    def test_map_is_mapn1(self):
        """
        Ensure that algo.map() is functionally identical to algo.mapn()
        with only one column.
        """
        LEN=10
        col = [*range(LEN)]
        fct = lambda x : x*2

        map_result = eval(self, algo.map(fct), col)
        mapn_result = eval(self, algo.mapn(fct), col)

        self.assertSequenceEqual(map_result, mapn_result)

# ======================================================================
# Calendar functions
# ======================================================================
from fin.seq import table
import ast
class TestCalendarFunctions(unittest.TestCase):
    def test_shift_data(self):
        t = table.table_from_csv_file("tests/_fixtures/^FCHI.csv", "d")
        with open("tests/_fixtures/shift_date.py") as f:
            expected = ast.literal_eval(f.read())

        t.add_column("Date2", (algo.shift_date(dict(years=1)), "Date"))
        l1 = list(map(str, t._meta[0]))
        l2 = list(map(str, t._meta[1]))
        actual = (*zip(l1, l2),)

        self.assertEqual(actual, expected)
