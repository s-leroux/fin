import unittest

import fin.seq.generator as generator

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
