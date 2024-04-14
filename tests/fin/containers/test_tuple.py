import sys
import unittest

from fin.containers import Tuple

class TestTuple(unittest.TestCase):
    def test_create(self):
        t = Tuple.create(5, "ABCDE")
        self.assertEqual(len(t), 5)
        self.assertSequenceEqual(t, "ABCDE")

    def test_dealloc(self):
        a = object()
        rca = sys.getrefcount(a)

        t = Tuple.create(5, (a,a,a,a,a))
        self.assertEqual(sys.getrefcount(a), rca + 5)

        t.__del__() # We shouldn't crash :/
        self.assertEqual(sys.getrefcount(a), rca)

    def test_set_get_item(self):
        """ Test get/set item; check the object's refernce count are consistent.
        """
        a = object()
        b = object()
        c = object()
        d = object()
        e = object()
        rca = sys.getrefcount(a)
        rcb = sys.getrefcount(b)
        rcc = sys.getrefcount(c)
        rcd = sys.getrefcount(d)
        rce = sys.getrefcount(e)

        t = Tuple.create(5, (a,b,c,d,e))
        self.assertEqual(sys.getrefcount(a), rca+1)
        self.assertEqual(sys.getrefcount(b), rcb+1)
        self.assertEqual(sys.getrefcount(c), rcc+1)
        self.assertEqual(sys.getrefcount(d), rcd+1)
        self.assertEqual(sys.getrefcount(e), rce+1)

        self.assertEqual(len(t), 5)
        self.assertEqual(t[2], c)
        self.assertSequenceEqual(t, (a,b,c,d,e))

        t.__del__()
        self.assertEqual(sys.getrefcount(a), rca)
        self.assertEqual(sys.getrefcount(b), rcb)
        self.assertEqual(sys.getrefcount(c), rcc)
        self.assertEqual(sys.getrefcount(d), rcd)
        self.assertEqual(sys.getrefcount(e), rce)

    def test_new_view(self):
        a = object()
        b = object()
        rca = sys.getrefcount(a)
        rcb = sys.getrefcount(b)

        t = Tuple.create(4, (a,a,b,b))
        self.assertEqual(sys.getrefcount(a), rca + 2)
        self.assertEqual(sys.getrefcount(b), rcb + 2)

        u = t.new_view(1,3)
        self.assertEqual(sys.getrefcount(a), rca + 2)
        self.assertEqual(sys.getrefcount(b), rcb + 2)

        self.assertSequenceEqual(u, (a,b))

    def test_remap(self):
        a = object()
        b = object()
        c = object()
        d = object()
        e = object()
        X = None
        t = Tuple.create(5, (a, b, c, d, e))
        #                    0  1  2  3  4
        usecases = (
            "#0 identity",
            ( 0, 1, 2, 3, 4),
            ( a, b, c, d, e),
            "#1 reorder, same size",
            ( 1, 4, 3, 2, 0),
            ( b, e, d, c, a),
            "#2 reorder, shorter",
            ( 1, 4, 0),
            ( b, e, a),
            "#3 reorder, longuer",
            ( 1, 4, 3, 2, 0, 3, 4, 2, 1),
            ( b, e, d, c, a, d, e, c, b),
            "#4 reorder, longuer with holes",
            ( 1, 4,-1, 2, 0,-1, 4, 2, 1),
            ( b, e, X, c, a, X, e, c, b),
                )

        while usecases:
            desc, mapping, expected, *usecases = usecases
            with self.subTest(desc=desc):
                u = t.remap(mapping)
                self.assertSequenceEqual(u, expected)

    def test_resize_grow(self):
        a = object()
        rca = sys.getrefcount(a)

        t = Tuple.create(5, (a,a,a,a,a))
        self.assertEqual(sys.getrefcount(a), rca + 5)

        t.tst_resize(10)
        self.assertEqual(sys.getrefcount(a), rca + 5)
        self.assertSequenceEqual(t, (a,)*5 + (None,)*5)

        t.__del__() # We shouldn't crash :/
        self.assertEqual(sys.getrefcount(a), rca)

    def test_resize_shrink(self):
        a = object()
        rca = sys.getrefcount(a)

        t = Tuple.create(5, (a,a,a,a,a))
        self.assertEqual(sys.getrefcount(a), rca + 5)

        t.tst_resize(3)
        self.assertEqual(sys.getrefcount(a), rca + 3)
        self.assertSequenceEqual(t, (a,a,a))

        t.__del__() # We shouldn't crash :/
        self.assertEqual(sys.getrefcount(a), rca)

    def test_from_sequence(self):
        N = 1000
        def g():
            for i in range(N):
                yield i

        usecases = (
                "#0 From generator",
                g(),
                "#1 From list",
                list(range(N)),
                "#2 From tuple",
                tuple(range(N)),
            )
        
        while usecases:
            desc, src, *usecases = usecases
            with self.subTest(desc=desc):
                t = Tuple.from_sequence(src)
                self.assertSequenceEqual(t, (range(N)))

    def test_from_constant(self):
        N = 100
        a = object()
        rca = sys.getrefcount(a)

        t = Tuple.from_constant(N, a)
        self.assertEqual(sys.getrefcount(a), rca + N)
        self.assertSequenceEqual(t, (a,)*N)

