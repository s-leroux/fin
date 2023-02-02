import unittest

from fin.ptree import ptree


def assertTreeEqual(self,a,b):
    def round(x):
        return "{:.4f}".format(x)

    msg = "\n{:}\n{:}".format(a, b)

    self.assertEqual(len(a), len(b), "Different list length" + msg)
    for a, b in zip(a, b):
        self.assertEqual(list(map(round, a)), list(map(round, b)),
                "Different list element {} and {}{}".format(a, b, msg))

unittest.TestCase.assertTreeEqual = assertTreeEqual

class TestPTree(unittest.TestCase):
    def ptree(self, n):
        tenth = lambda x: x/10
        return ptree(tenth, n, 1000, [[0.7, 1100],[0.3,  900]])

    def test_0_iter(self):
        p = self.ptree(0)
        self.assertTreeEqual(p, [(100, 1000, 1.0)])

    def test_1_iter(self):
        p = self.ptree(1)
        self.assertTreeEqual(p, [
            (90, 900, 0.3),
            (110, 1100, 0.7),
        ])

    def test_2_iter(self):
        p = self.ptree(2)
        self.assertTreeEqual(p, [
            (81, 810, 0.09),
            (99, 990, 0.21),
            (99, 990, 0.21),
            (121, 1210, 0.49),
        ])

    def test_3_iter(self):
        p = self.ptree(3)
        self.assertTreeEqual(p, [
            (72.9, 729, 0.027),
            (89.1, 891, 0.063),
            (89.1, 891, 0.126),
            (108.9, 1089, 0.294),
            (108.9, 1089, 0.147),
            (133.1, 1331, 0.343),
        ])


class TestPTreeZero(unittest.TestCase):
    def ptree(self, n):
        tenth = lambda x: 0 if x <= 900 else x/10
        return ptree(tenth, n, 1000, [[0.7, 1100],[0.3,  900]])

    def test_0_iter(self):
        p = self.ptree(0)
        self.assertTreeEqual(p, [(100, 1000, 1.0)])

    def test_1_iter(self):
        p = self.ptree(1)
        self.assertTreeEqual(p, [
            (0, 900, 0.3),
            (110, 1100, 0.7),
        ])

    def test_2_iter(self):
        p = self.ptree(2)
        self.assertTreeEqual(p, [
            (0, 900, 0.3),
            (99, 990, 0.21),
            (121, 1210, 0.49),
        ])

    def test_3_iter(self):
        p = self.ptree(3)
        self.assertTreeEqual(p, [
            (0, 891, 0.063),
            (0, 900, 0.3),
            (108.9, 1089, 0.294),
            (133.1, 1331, 0.343),
        ])

