import unittest

from . import functor

from tests.fin.seq2.fc import utilities

# ======================================================================
# Functors
# ======================================================================
class TestFunctor(unittest.TestCase):
    def test_functor(self):
        f = functor.Functor1Example()

