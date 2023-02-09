import unittest

from fin.seq import algo

class TestWindow(unittest.TestCase):
    def test_one_column(self):
        cols = [
            list(range(10, 20)),
        ]

        fct = algo.naive_window(sum, 2)
        actual = fct(len(cols[0]), *cols)

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
        cols = [
            list(range(10, 20)),
        ]

        fct = algo.moving_average(2)
        actual = fct(len(cols[0]), *cols)

        self.assertSequenceEqual(actual, [ None, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5 ])

