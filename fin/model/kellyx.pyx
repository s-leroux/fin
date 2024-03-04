# cython: boundscheck=False
# cython: cdivision=True
# cython: binding=True

from libc.math cimport log
from fin.mathx cimport alloc

"""
Cython implementation of the Kelly Criterion.
"""
cpdef double kelly_criterion(double p, double a, double b, double f_star):
    """
    Model for the general form of the Kelly formula.
    
    From https://en.wikipedia.org/wiki/Kelly_criterion:
    ``f^{*}`` is the fraction of the assets to apply to the security.
    ``p`` is the probability that the investment increases in value.
    ``q`` is the probability that the investment decreases in value (implied since ``q = 1−p``).
    ``a`` a is the fraction that is lost in a negative outcome. If the security price falls 10%, then a = 0.1
    ``b`` is the fraction that is gained in a positive outcome. If the security price rises 10%, then b = 0.1.
    """
    cdef double q = 1.0-p
    return p/a - (1-p)/b - f_star

cdef class Experiment:
    cdef unsigned _exp1_len
    cdef double[::1]  _exp1_prob
    cdef double[::1]  _exp1_gain
    cdef unsigned _exp2_len
    cdef double[::1]  _exp2_prob
    cdef double[::1]  _exp2_gain

    def __init__(self, exp1_iter, exp2_iter):
        # We materialized the iteratorss as tuples since we need
        # the size for array allocation
        cdef tuple exp1 = tuple(exp1_iter)
        cdef tuple exp2 = tuple(exp2_iter)
        cdef unsigned exp1_len = len(exp1)
        cdef unsigned exp2_len = len(exp2)

        self._exp1_len = exp1_len
        self._exp2_len = exp2_len
        self._exp1_prob = alloc(exp1_len)
        self._exp1_gain = alloc(exp1_len)
        self._exp2_prob = alloc(exp2_len)
        self._exp2_gain = alloc(exp2_len)

        cdef unsigned i

        i = 0
        for p,g in exp1:
            self._exp1_prob[i] = p
            self._exp1_gain[i] = g

            i+=1

        for i in range(exp2_len):
            self._exp2_prob[i], self._exp2_gain[i] = exp2[i]

    cdef double _growth(self, double p, double wealth = 1):
        """
        Compute the log of the expected return.

        E log(X)
        """
        cdef unsigned i1
        cdef unsigned i2

        cdef double q = 1-p
        cdef double acc = 0.0
        cdef double x
        for i1 in range(self._exp1_len):
            for i2 in range(self._exp2_len):
                x = wealth*(self._exp1_gain[i1]*p + self._exp2_gain[i2]*q)
                acc += self._exp1_prob[i1]*self._exp2_prob[i2]*log(x)

        return acc

    cpdef growth(self, double p, double wealth=1):
        return self._growth(p, wealth)
