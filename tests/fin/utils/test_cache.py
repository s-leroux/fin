import unittest

import os

from fin.utils.cache import SqliteCacheProvider

SQLITE_CACHE_PATH = "my-cache.sqlite3"

def fct(x,y, *, z):
    return x+10*y+100*z

class TestCache(unittest.TestCase):
    def setUp(self):
        try:
            os.unlink(SQLITE_CACHE_PATH)
        except FileNotFoundError:
            pass

    def test_cache(self):
        cache = SqliteCacheProvider(SQLITE_CACHE_PATH)
        cached = cache(fct)

        self.assertEqual(cache.miss, 0)
        self.assertEqual(cache.hit, 0)

        a = cached(1,2,z=3)

        self.assertEqual(cache.miss, 1)
        self.assertEqual(cache.hit, 0)

        b = cached(1,2,z=3)

        self.assertEqual(a, b)

        self.assertEqual(cache.miss, 1)
        self.assertEqual(cache.hit, 1)

        c = cached(1,2,z=3)

        self.assertEqual(cache.miss, 1)
        self.assertEqual(cache.hit, 2)

    def test_cache_persistance(self):
        try:
            cache = SqliteCacheProvider(SQLITE_CACHE_PATH)
            cached = cache(fct)

            self.assertEqual(cache.miss, 0)
            self.assertEqual(cache.hit, 0)

            a = cached(1,2,z=3)

            self.assertEqual(cache.miss, 1)
            self.assertEqual(cache.hit, 0)
        finally:
            cache.close()

        try:
            cache = SqliteCacheProvider(SQLITE_CACHE_PATH)
            cached = cache(fct)

            self.assertEqual(cache.miss, 0)
            self.assertEqual(cache.hit, 0)

            b = cached(1,2,z=3)

            self.assertEqual(cache.miss, 0)
            self.assertEqual(cache.hit, 1)
        finally:
            cache.close()

        self.assertEqual(a, b)
