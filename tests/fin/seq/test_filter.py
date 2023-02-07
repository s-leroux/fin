import unittest

from fin.seq import source
from fin.seq import filter
from fin.seq import sink

class TestChunked(unittest.TestCase):
    def test_chunked(self):
        SIZE=10
        g = source.range(500)
        g = filter.chunked(g, SIZE)
        for i in range(50):
            chunk, g = g(i)
            if chunk:
                self.assertLessEqual(len(chunk[0]), SIZE)

class TestFuse(unittest.TestCase):
    def test_fuse_1(self):
        a = filter.chunked(source.constant(1), 10)
        b = filter.chunked(source.constant(2), 3)
        ab = filter.fuse(a,b)

        for i in range(1,20):
            msg = "at step {}".format(i)
            data, _ = sink.take(ab, i)
            self.assertEqual(len(data), 2, msg)
            for col in data:
                self.assertEqual(len(col), i, msg)

    def test_fuse_2(self):
        ca = tuple(range(100,200))
        cb = tuple(range(200,300))

        a = filter.chunked(source.rawdata((ca,)), 10)
        b = filter.chunked(source.rawdata((cb,)), 3)
        ab = filter.fuse(a,b)

        data = sink.all(ab)
        self.assertEqual(len(data), 2)
        self.assertEqual(data, (ca, cb))
