import unittest

import random
from fin.seq import algo

ROUNDING=8
def eval(fct, *cols):
    try:
        nrows = len(cols[0])
    except IndexError:
        # Fallback in case we want to test zero-column expressions.
        nrows = 10

    result = fct(nrows, *cols)
    return [round(x, ROUNDING) if type(x) is float else x for x in result]

class TestWindow(unittest.TestCase):
    def test_one_column(self):
        actual = eval(
            algo.naive_window(sum, 2),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [ None, 21, 23, 25, 27, 29, 31, 33, 35, 37 ])

class TestByRow(unittest.TestCase):
    def test_by_row(self):
        LEN=10
        A=list(range(100,100+LEN))
        B=list(range(200,200+LEN))
        cols = [ A, B ]

        fct = algo.by_row(lambda a,b: a+b)
        actual = fct(LEN, A, B)

        self.assertSequenceEqual(actual, list(range(300, 300+2*LEN, 2)))

class Test_Sum(unittest.TestCase):
    def test__sum(self):
        from fin.seq.algox import _Sum
        actual = eval(
            _Sum(4),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [None, None, None, 46.0, 50.0, 54.0, 58.0, 62.0, 66.0, 70.0])

class TestMul(unittest.TestCase):
    def test_mul(self):
        actual = eval(
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
        actual = eval(
            algo.mul(),
            lst,
        )
        self.assertSequenceEqual(actual, lst)

    def test_mul_zero_columns(self):
        actual = eval(
            algo.mul(),
        )
        self.assertSequenceEqual(actual, [1.0]*10)


class TestDiv(unittest.TestCase):
    def test_div(self):
        a = [*range(0,10)]
        b = [*range(10,20)]
        c = [*range(100,110)]
        actual = eval(
            algo.div(),
            [x*y*z for x,y,z in zip(a,b,c)],
            b,
            c,
        )

        self.assertSequenceEqual(actual, a);

    def test_div_one_columns(self):
        lst = [*range(0,10)]
        actual = eval(
            algo.div(),
            lst,
        )
        self.assertSequenceEqual(actual, [float("inf"), *(round(1/x,8) for x in lst[1:])])

    def test_div_zero_columns(self):
        actual = eval(
            algo.div(),
        )
        self.assertSequenceEqual(actual, [None]*10)

class TestSub(unittest.TestCase):
    def test_sub(self):
        actual = eval(
            algo.sub(),
            [*range(100,110)],
            [*range(10,20)],
            [*range(0,10)],
        )

        self.assertSequenceEqual(actual, [90.0, 89.0, 88.0, 87.0, 86.0, 85.0, 84.0, 83.0, 82.0, 81.0])

    def test_sub_one_columns(self):
        lst = [*range(0,10)]
        actual = eval(
            algo.sub(),
            lst,
        )
        self.assertSequenceEqual(actual, [-x for x in lst])


    def test_sub_zero_columns(self):
        actual = eval(
            algo.sub(),
        )
        self.assertSequenceEqual(actual, [0.0]*10)


class TestSub(unittest.TestCase):
    def test_sub(self):
        actual = eval(
            algo.sub(),
            [*range(100,110)],
            [*range(10,20)],
            [*range(0,10)],
        )

        self.assertSequenceEqual(actual, [90.0, 89.0, 88.0, 87.0, 86.0, 85.0, 84.0, 83.0, 82.0, 81.0])

    def test_sub_one_columns(self):
        lst = [*range(0,10)]
        actual = eval(
            algo.sub(),
            lst,
        )
        self.assertSequenceEqual(actual, [-x for x in lst])


    def test_sub_zero_columns(self):
        actual = eval(
            algo.sub(),
        )
        self.assertSequenceEqual(actual, [0.0]*10)

class TestSimpleMovingAverage(unittest.TestCase):
    def test_sma(self):
        actual = eval(
            algo.sma(2),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [ None, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5 ])

class TestExponentialMovingAverage(unittest.TestCase):
    def test_ema(self):
        actual = eval(
            algo.ema(3),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [
           None,
           None,
           None,
           12.125, # XXX should we discard that value or not?
           13.0625,
           14.03125,
           15.015625,
           16.0078125,
           17.00390625,
           18.00195312,
         ])

    def test_ema_reset(self):
        """ ema hould reset if it encounters a `None` value.
        """
        data = list(range(10, 20))
        data[5] = None
        actual = eval(
            algo.ema(3),
            data,
        )

        self.assertSequenceEqual(actual, [
           None,
           None,
           None,
           12.125,
           13.0625,
           None,
           None,
           None,
           None,
           18.125,
         ])

class TestWildersSmoothing(unittest.TestCase):
    def test_wilders(self):
        tests = [
            [
                "from 'Technical Analysis from A to Z, 2nd edition', p366",
                5, # window size
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
                "from https://github.com/TulipCharts/tulipindicators/blob/master/tests/untest.txt",
                5, # window size
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
                "missing data",
                5, # window size
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
        for (desc, size, precision, *data) in tests:
            with self.subTest(desc=desc):
                src = data[::2]
                expected = data[1::2]
                actual = eval(algo.wilders(size), src)
                actual = [x and round(x, precision) for x in actual]
                self.assertSequenceEqual(actual, expected)

class TestStandardDeviation(unittest.TestCase):
    def test_standard_deviation(self):
        actual = eval(
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
        actual = eval(
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

        actual = eval(
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
        actual = eval(
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
        actual = eval(
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

        actual = eval(algo.volatility(WINDOW), INPUT)

        self.assertSequenceEqual(actual, OUTPUT)

class TestBestFit(unittest.TestCase):
    def test_best_fit(self):
        actual = eval(
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

        actual = eval(algo.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual, EXPECTED)

    def test_beta_x10(self):
        LEN = 100
        WINDOW = 10
        COL_X = [*range(LEN)]
        COL_Y = [x*10 for x in COL_X]
        EXPECTED = [None]*(WINDOW-1) + [10.0]*(LEN-WINDOW+1)

        actual = eval(algo.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual, EXPECTED)

    def test_beta_neg(self):
        LEN = 100
        WINDOW = 10
        COL_X = [*range(LEN)]
        COL_Y = [-x for x in COL_X]
        EXPECTED = [None]*(WINDOW-1) + [-1.0]*(LEN-WINDOW+1)

        actual = eval(algo.beta(WINDOW), COL_X, COL_Y)

        self.assertSequenceEqual(actual, EXPECTED)

class TestMapChange(unittest.TestCase):
    def test_map_change(self):
        INPUT=list(range(1,10))
        OUTPUT = [None, *range(3, 19, 2)]

        actual = eval(algo.map_change(lambda a,b: a+b), INPUT)

        self.assertSequenceEqual(actual, OUTPUT)

class TestMapN(unittest.TestCase):
    def test_map_n_0(self):
        LEN=10
        A = list(range(0, LEN))
        B = list(range(1, LEN+1))
        F=lambda a,b: a+b
        EXPECTED = list(range(1, 2*LEN+1, 2))
        actual = eval(algo.mapn(F), A, B)

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
                        actual = eval(algo.line(a,b), X, Y)
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
        actual = eval(algo.shift(-DELTA), self._list)

        self.assertSequenceEqual(actual, EXPECTED)

    def test_shift_pos(self):
        DELTA=3
        EXPECTED = self._list[DELTA:] + [None]*DELTA
        actual = eval(algo.shift(DELTA), self._list)

        self.assertSequenceEqual(actual, EXPECTED)

class TestMax(unittest.TestCase):
    def test_max(self):
        l = [1, 3, 3, 2, 4, 5, 3, 1, 1, 1, 1]
        expected = [None, None, 3, 3, 4, 5, 5, 5, 3, 1, 1]
        actual = eval(algo.max(3), l)

        self.assertSequenceEqual(actual, expected)

    def test_max_none(self):
        l = [1, 3, 3, 2, 4, 5, None, 1, 1, 1, 1]
        expected = [None, None, 3, 3, 4, 5, None, None, None, 1, 1]
        actual = eval(algo.max(3), l)

        self.assertSequenceEqual(actual, expected)

class TestMin(unittest.TestCase):
    def test_min(self):
        l = [1, 3, 3, 2, 4, 5, 3, 1, 1, 1, 1]
        expected = [None, None, 1, 2, 2, 2, 3, 1, 1, 1, 1]
        actual = eval(algo.min(3), l)

        self.assertSequenceEqual(actual, expected)

    def test_min(self):
        l = [1, 3, 3, 2, 4, 5, None, 1, 1, 1, 1]
        expected = [None, None, 1, 2, 2, 2, None, None, None, 1, 1]
        actual = eval(algo.min(3), l)

        self.assertSequenceEqual(actual, expected)

class TestRatio(unittest.TestCase):
    def test_ratio(self):
        L=10
        colA = list(range(-L, L+1))
        colB = list(range(1,2*L+2))

        expected = [round(a_i/b_i, ROUNDING) for a_i, b_i in zip(colA, colB)]
        actual = eval(algo.ratio, colA, colB)

        self.assertSequenceEqual(actual, expected)

    def test_ratio_inf_undef(self):
        L=10
        colA = list(range(-L, L+1))
        colB = [0.0]*(2*L+1)

        expected = [float("-inf")]*L + [None] + [float("inf")]*L
        actual = eval(algo.ratio, colA, colB)

        self.assertSequenceEqual(actual, expected)

class TestDelta(unittest.TestCase):
    def test_delta(self):
        LEN=10
        col = [*range(LEN)]

        expected = [None] + [1]*(LEN-1)
        actual = eval(algo.delta(), col)

        self.assertSequenceEqual(actual, expected)

    def test_delta_with_none(self):
        LEN=10
        IDX=5
        col = [*range(LEN)]
        col[IDX] = None

        expected = [None] + [1]*(LEN-1)
        expected[IDX] = None
        expected[IDX+1] = None
        actual = eval(algo.delta(), col)

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

        map_result = eval(algo.map(fct), col)
        mapn_result = eval(algo.mapn(fct), col)

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
