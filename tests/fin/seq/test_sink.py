import unittest

import fin.seq.source as source
import fin.seq.sink as sink

class TestCount(unittest.TestCase):
    def test_count(self):
        n = 2048
        l = ((1,)*n,)
        g = source.rawdata(l)

        self.assertEqual(sink.count(g), n)

class TestAll(unittest.TestCase):
    def test_all(self):
        l = ((1,2), (3,4), (5,6))
        g = source.rawdata(l)

        self.assertEqual(sink.all(g), l)

class TestConsumeAll(unittest.TestCase):
    def test_consume_all(self):
        n = 2048
        l = ((1,)*n,)
        g = source.rawdata(l)
        g = sink.consumeall(g)

        data, g = g(1)
        self.assertEqual(data, ())

