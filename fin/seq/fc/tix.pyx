# cython: boundscheck=False
# cython: cdivision=True

"""
Cython implementation of common algorithms on columns.
"""
from __future__ import print_function
# Above ^^^^^^^^^^^^^^^^^^^^:
# Cython 0.26.1 does not recognize the Python3 semantic for the print()
# function without that import.
# See: https://stackoverflow.com/questions/19185338/cython-error-compiling-with-print-function-parameters

from libc.math cimport sqrt
import array
from cpython cimport array

from fin.mathx cimport alloc, aalloc, isnan, NaN
from fin.seq cimport column
from fin.seq import column

from fin.seq.fc cimport funcx
from fin.seq.fc cimport statx

# ======================================================================
# Moving averages and smoothing functions
# ======================================================================
cdef class sma(funcx.Functor1):
    """
    Compute the Simple Moving Average over a n-period window.
    """
    def __cinit__(self):
        self.src1_tc = b'd'
        self.dst1_tc = b'd'

    cdef unsigned n

    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return f"SMA({self.n})"

    cdef void eval(self, unsigned l, funcx.param_t* dst, const funcx.param_t* src):
        cdef unsigned n = self.n

        cdef double[::1] buffer = alloc(n)
        cdef unsigned idx=0

        cdef double acc = 0.0
        cdef unsigned nans = n
        cdef double old, new
        cdef unsigned i
        for i in range(l):
            old = buffer[idx]
            if isnan(old):
                nans -= 1
            else:
                acc -= old

            buffer[idx] = new = src.as_doubles[i]
            idx += 1
            if idx == n:
                idx = 0

            if isnan(new):
                nans += 1
            else:
                acc += new

            dst.as_doubles[i] = NaN if nans else acc/n

cdef class ema(funcx.Functor1):
    """
    Compute the Exponential Moving Average over a n-period window.

    The smoothing factor is assumed to be `2/(1+n)` where `n` is the window size.
    """
    def __cinit__(self):
        self.src1_tc = b'd'
        self.dst1_tc = b'd'

    cdef unsigned n
    cdef double alpha

    def __init__(self, n):
        self.n = n
        self.alpha = 2.0/(1+n)

    def __repr__(self):
        return f"EMA({self.n})"

    cdef void eval(self, unsigned l, funcx.param_t* dst, const funcx.param_t* src):
        cdef unsigned n = self.n
        cdef double alpha = self.alpha

        cdef double acc = NaN
        cdef unsigned history = 0
        cdef double curr
        cdef unsigned i
        for i in range(l):
            curr = src.as_doubles[i]
            if isnan(acc):
                history = 0
                acc = curr
            elif isnan(curr):
                history = 0
                acc = NaN
            else:
                acc += (curr-acc)*alpha
                history += 1

            dst.as_doubles[i] = NaN if history<n else acc


cdef class wilders(funcx.Functor1):
    """
    Compute the Wilder's Smoothing.

    Except for the initialization stage, a `n` periode Wilder's Smoothing is equivalent
    to a `2n-1` Exponential Moving Average.
    """
    def __cinit__(self):
        self.src1_tc = b'd'
        self.dst1_tc = b'd'

    cdef unsigned n
    cdef double alpha

    def __init__(self, n):
        self.n = n
        self.alpha = 1.0/n

    def __repr__(self):
        return f"WILDERS({self.n})"

    cdef void eval(self, unsigned l, funcx.param_t* dst, const funcx.param_t* src):
        cdef unsigned n = self.n
        cdef double alpha = self.alpha

        cdef double acc = 0.0
        cdef unsigned history = 0
        cdef double curr
        cdef unsigned i
        for i in range(l):
            curr = src.as_doubles[i]
            if isnan(curr):
                history = 0
                acc = 0.0
            else:
                if history<n:
                    acc += curr*alpha
                else:
                    acc += (curr-acc)*alpha
                history += 1

            dst.as_doubles[i] = NaN if history<n else acc

# ======================================================================
# Technical Indicators
# ======================================================================
cdef class Tr(funcx.Functor3):
    """
    Compute the True Range

    On day `i`, the True Range is the greatest of:
    * `high[i]-low[i]`
    * `abs(high[i]-close[i-1])`
    * `abs(low[i]-close[i-1])`
    """
    def __cinit__(self):
        self.src1_tc = b'd'
        self.src2_tc = b'd'
        self.src3_tc = b'd'
        self.dst1_tc = b'd'

    def __repr__(self):
        return f"TR"

    cdef void eval(self, unsigned l, funcx.param_t *dst, const funcx.param_t* high, const funcx.param_t* low, const funcx.param_t* close):
        cdef double yc = NaN # Yesterday's close
        cdef double th # today's high
        cdef double tl # today's low

        cdef double hc
        cdef double lc

        cdef double tr

        cdef unsigned i
        for i in range(l):
            th = high.as_doubles[i]
            tl = low.as_doubles[i]

            tr = th-tl
            if not isnan(yc):
                hc = abs(th-yc)
                lc = abs(tl-yc)

                if hc > tr:
                    tr = hc
                if lc > tr:
                    tr = lc

            dst.as_doubles[i] = tr
            yc = close.as_doubles[i]

tr = Tr()

class atr(funcx.Functor3):
    """
    Compute the Average True Range.

    The Average True Range is the smoothed value of the True Range indicator.
    
    This indicator uses the Wilder's Smoothing.
    Potentially this could be parameterized.
    """
    def __init__(self, n):
        self.n = n
        self.tr = tr
        self.smooth = wilders(n)

    def __repr__(self):
        return f"ATR({self.n})"

    def __call__(self, rowcount, high, low, close):
        tr = self.tr(rowcount, high, low, close)
        atr = self.smooth(rowcount, tr)
        return atr

cdef class band(funcx.Functor2_3):
    """
    Compute a band arround a middle value.
    """
    cdef double _width

    def __cinit__(self):
        self.src1_tc = b'd'
        self.src2_tc = b'd'
        self.dst1_tc = b'd'
        self.dst2_tc = b'd'
        self.dst3_tc = b'd'

    def __init__(self, width):
        self._width = width

    cdef make_names(self, col1, col2):
        basename = col1.name
        return [
                f"{basename}:B",
                f"{basename}:M",
                f"{basename}:A",
                ]

    cdef void eval(self, unsigned l,
            funcx.param_t *dst1, funcx.param_t *dst2, funcx.param_t *dst3,
            const funcx.param_t *src1, const funcx.param_t *src2):
        cdef double width = self._width
        cdef unsigned i
        for i in range(l):
            dst1.as_doubles[i] = src1.as_doubles[i]-width*src2.as_doubles[i]
            dst2.as_doubles[i] = src1.as_doubles[i]
            dst3.as_doubles[i] = src1.as_doubles[i]+width*src2.as_doubles[i]

cdef class bband(funcx.Functor1_3):
    """
    Compute the Bollinger's band.
    """
    def __cinit__(self):
        self.src1_tc = b'd'
        self.dst1_tc = b'd'
        self.dst2_tc = b'd'
        self.dst3_tc = b'd'

    cdef sma _sma
    cdef statx.stdev _stdev
    cdef band _band
    cdef unsigned _n

    def __init__(self, n, w=2):
        self._sma = sma(n)
        self._stdev = statx.stdev.p(n)
        # Above:
        # in "Bollinger on Bollinger's Bands" p52 John Bollinger uses the population 
        # formula for standard deviation.
        self._band = band(2)
        self._n = n

    cdef make_names(self, col1):
        n = self._n
        width = self._band._width
        basename = col1.name
        return [
                f"BBANDB({n},{width}) {basename}",
                f"{self._sma.make_name(col1)}",
                f"BBANDT({n},{width}) {basename}",
                ]

    cdef void eval(self, unsigned l,
            funcx.param_t *dst1, funcx.param_t *dst2, funcx.param_t *dst3,
            const funcx.param_t *src1):
        cdef double[::1] middle = alloc(l)
        cdef double[::1] sd = alloc(l)
        self._sma.eval(l, <funcx.param_t*>&middle[0], <funcx.param_t*>src1)
        self._stdev.eval(l, <funcx.param_t*>&sd[0], <funcx.param_t*>&middle[0])
        self._band.eval(l, dst1, dst2, dst3, <funcx.param_t*>&middle[0], <funcx.param_t*>&sd[0])

