import unittest

import fin.seq.generator as generator
import fin.seq.sink as sink

class TestUtils(unittest.TestCase):
    def test_samples(self):
        l = [(1,2), (3,4)]
        expected = tuple(l)
        actual = generator.samples(l)

        self.assertEqual(actual, expected)

class TestConstant(unittest.TestCase):
    def test_const_value(self):
        g = generator.constant(1)
        for n in 5,6,7:
            actual, g = g(n)
            self.assertSequenceEqual(actual, ((1,),)*n)

    def test_const_values(self):
        g = generator.constant(1,2,3)
        for n in 5,6,7:
            actual, g = g(n)
            self.assertSequenceEqual(actual, ((1,2,3,),)*n)

class TestRawData(unittest.TestCase):
    def test_data(self):
        data = ((1,2),(3,4),(5,6),(7,8))
        g = generator.rawdata(data)
        result = []

        for i in range(1,6):
            chunk, g = g(i)
            result.extend(chunk)

        self.assertSequenceEqual(tuple(result), data)

    def test_const_values(self):
        g = generator.constant(1,2,3)
        for n in 5,6,7:
            actual, g = g(n)
            self.assertSequenceEqual(actual, ((1,2,3,),)*n)

class TestRange(unittest.TestCase):
    def expected(self, a, b=None, c=None):
        result = []
        r = None
        if c is not None:
            r = range(a, b, c)
        elif b is not None:
            r = range(a, b)
        else:
            r = range(a)

        for n in r:
            result.append((n,))

        return result

    def test_range_1(self):
        expected = self.expected(1000)
        g = generator.range(1000)
        actual = sink.all(g) 

        self.assertSequenceEqual(actual, expected)

    def test_range_2(self):
        expected = self.expected(1, 100)
        g = generator.range(1, 100)
        actual = sink.all(g) 

        self.assertSequenceEqual(actual, expected)

    def test_range_3(self):
        expected = self.expected(1, 2000, 3)
        g = generator.range(1, 2000, 3)
        actual = sink.all(g) 

        self.assertSequenceEqual(actual, expected)

    def test_range_idempotence(self):
        n = 3
        expected = self.expected(1, n+1)
        g = generator.range(1, 100)
        a = sink.take(g, n)
        b = sink.take(g, n)

        self.assertSequenceEqual(a, expected)
        self.assertSequenceEqual(a, b)

