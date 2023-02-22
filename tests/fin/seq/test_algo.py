import unittest

from fin.seq import algo

def eval(fct, *cols):
    result = fct(len(cols[0]), *cols)
    return [round(x, 8) if type(x) is float else x for x in result]

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


class TestMovingAverage(unittest.TestCase):
    def test_moving_average(self):
        actual = eval(
            algo.moving_average(2),
            list(range(10, 20)),
        )

        self.assertSequenceEqual(actual, [ None, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5 ])


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

    def test_naive_standard_deviation(self):
        """ check if the default implementation is consistent with
            the naive implementation
        """
        WINDOW_SIZE=4
        vector = [x**2 for x in range(10, 20)]
        s1 = eval(
            algo.naive_standard_deviation(WINDOW_SIZE),
            vector,
        )
        s2 = eval(
            algo.standard_deviation(WINDOW_SIZE),
            vector,
        )

        self.assertSequenceEqual(s1, s2)

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


class TestMap1(unittest.TestCase):
    def test_map1(self):
        INPUT=list(range(1,10))
        OUTPUT = [None, *range(3, 19, 2)]

        actual = eval(algo.map1(lambda a,b: a+b), INPUT)

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

        t.add_column("Date2", algo.shift_date(years=1), "Date")
        l1 = list(map(str, t._meta[1]))
        l2 = list(map(str, t._meta[2]))
        actual = (*zip(l1, l2),)

        self.assertEqual(actual, expected)
