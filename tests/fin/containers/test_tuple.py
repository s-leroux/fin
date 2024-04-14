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
        rca = sys.getrefcount(a)
        rcb = sys.getrefcount(b)

        t = Tuple.create(5, (a,a,a,a,a))
        self.assertEqual(sys.getrefcount(b), rcb)
        self.assertEqual(sys.getrefcount(a), rca+5)

        t[2] = b
        self.assertEqual(sys.getrefcount(b), rcb+1)
        self.assertEqual(sys.getrefcount(a), rca+4)

        t[2] = b
        self.assertEqual(sys.getrefcount(b), rcb+1)
        self.assertEqual(sys.getrefcount(a), rca+4)

        self.assertEqual(len(t), 5)
        self.assertEqual(t[2], b)
        self.assertSequenceEqual(t, (a,a,b,a,a))

        t.__del__()
        self.assertEqual(sys.getrefcount(b), rcb)
        self.assertEqual(sys.getrefcount(a), rca)

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

