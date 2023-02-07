import unittest

import fin.seq.source as source
import fin.seq.sink as sink

class TestUtils(unittest.TestCase):
    def test_samples(self):
        l = [(1,2), (3,4)]
        expected = tuple(l)
        actual = source.samples(l)

        self.assertEqual(actual, expected)

class TestConstant(unittest.TestCase):
    def test_const_value(self):
        g = source.constant(1)
        for n in 5,6,7:
            actual, g = g(n)
            self.assertSequenceEqual(actual, ((1,)*n,))

    def test_const_values(self):
        g = source.constant(1,2,3)
        for n in 5,6,7:
            expected = tuple((i,)*n for i in (1,2,3))
            actual, g = g(n)
            self.assertSequenceEqual(actual, expected)

class TestRawData(unittest.TestCase):
    def build_test_case(self, n):
        return [tuple(range(col, col+n)) for col in (100,200,300,400)]

    def test_data(self):
        data = self.build_test_case(25)
        g = source.rawdata(data)
        result = ((),)*len(data)

        for i in range(1,50):
            chunk, g = g(i)
            if chunk:
                result = tuple(a+b for a,b in zip(result, chunk))

        self.assertSequenceEqual(tuple(result), data)

class TestRange(unittest.TestCase):
    def test_range_1(self):
        expected = (tuple(range(1000)),)
        g = source.range(1000)
        actual = sink.all(g) 

        self.assertSequenceEqual(actual, expected)

    def test_range_2(self):
        expected = (tuple(range(1, 100)),)
        g = source.range(1, 100)
        actual = sink.all(g) 

        self.assertSequenceEqual(actual, expected)

    def test_range_3(self):
        expected = (tuple(range(1, 2000, 3)),)
        g = source.range(1, 2000, 3)
        actual = sink.all(g) 

        self.assertSequenceEqual(actual, expected)

    def test_range_idempotence(self):
        n = 3
        expected = (tuple(range(1, n+1)),)
        g = source.range(1, 100)
        a, _ = sink.take(g, n)
        b, _ = sink.take(g, n)

        self.assertSequenceEqual(a, expected)
        self.assertSequenceEqual(a, b)

