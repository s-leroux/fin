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

