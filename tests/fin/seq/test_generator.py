import unittest

import fin.seq.generator as generator

class TestContant(unittest.TestCase):
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
