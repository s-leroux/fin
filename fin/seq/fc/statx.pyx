# cython: boundscheck=False
# cython: cdivision=True

"""
Cython implementation of common algorithms on columns.
"""

from libc.math cimport sqrt
import array

from fin.mathx cimport alloc, aalloc, isnan, NaN
from fin.seq.column cimport Column
from fin.seq.serie cimport Serie
from fin cimport mem

# ======================================================================
# Math and stats
# ======================================================================
cdef class var:
    """
    Compute the Variance over a n-period window.

    This is an implementation of the naive algorithm which is not numerically
    stable in the general case, but this should be sufficient for financial data.

    This general implmentation allows for a correction parameter.
    """
    def __init__(self, *args, **wargs):
        raise NotImplementedError("Use a factory method, not a constructor")

    cdef init(self, unsigned n, double correction):
        self.a = 1.0/(n+correction)
        self.b = self.a/n
        self.n = n
        self.correction = correction

    @staticmethod
    def s(unsigned n):
        """
        Instanciate a functor to compute the unbiased sample variance.
        """
        res = var.__new__(var)
        var.init(res, n, -1)

        return res

    @staticmethod
    def p(unsigned n):
        """
        Instanciate a functor to compute the population variance.
        """
        res = var.__new__(var)
        var.init(res, n, -1)

        return res

    def __call__(self, Serie ser, Column col):
        # ------------------ prologue ------------------
        cdef unsigned l = ser.rowcount
        cdef double[::1] dst = mem.double_alloc(l)
        cdef const double *src = col.as_float_values()
        # -------------- end of prologue ---------------

        self.eval(l, &dst[0], src)

        # ------------------ epilogue ------------------
        return Column.from_float_mv(
                dst,
                name=f"{self}, {col.name}",
                type=col._type
            )
        # -------------- end of epilogue ---------------

    cdef void eval(self, unsigned l, double* dst, const double* src):
        cdef double a = self.a
        cdef double b = self.b
        cdef unsigned n = self.n

        cdef double sigma_ui = 0.0
        cdef double sigma_ui2 = 0.0
        cdef unsigned nones = 0
        cdef unsigned i = 0

        # degenerate case
        if l < n:
            return

        # general case
        while i < n-1:
            v = src[i]
            if not isnan(v):
                sigma_ui += v
                sigma_ui2 += v*v
            else:
                nones += 1

            dst[i] = NaN
            i += 1

        while i < l:
            v = src[i]
            if not isnan(v):
                sigma_ui += v
                sigma_ui2 += v*v
            else:
                nones += 1

            dst[i] = NaN if nones else a*sigma_ui2 - b*sigma_ui*sigma_ui

            i += 1

            v = src[i-n]
            if not isnan(v):
                sigma_ui -= v
                sigma_ui2 -= v*v
            else:
                nones -= 1

cdef class stdev:
    """
    Compute the Standard Deviation over a n-period window.

    The standard deviation is defined as the square root of the variance
    as implemented here.
    """
    def __init__(self, *args, **wargs):
        raise NotImplementedError("Use a factory method, not a constructor")

    cdef init(self, unsigned n, var v):
        self.delegate = v

    @staticmethod
    def s(unsigned n):
        """
        Instanciate a functor to compute the unbiased sample standard deviation.
        """
        cdef stdev res = stdev.__new__(stdev)
        res.init(n, var.s(n))

        return res

    @staticmethod
    def p(unsigned n):
        """
        Instanciate a functor to compute the population standard deviation.
        """
        cdef stdev res = stdev.__new__(stdev)
        res.init(n, var.p(n))

        return res

    def __repr__(self):
        return f"STDDEV({self.delegate.n})"

    def __call__(self, Serie ser, Column col):
        # ------------------ prologue ------------------
        cdef unsigned l = ser.rowcount
        cdef double[::1] dst = mem.double_alloc(l)
        cdef const double *src = col.as_float_values()
        # -------------- end of prologue ---------------

        self.eval(l, &dst[0], src)

        # ------------------ epilogue ------------------
        return Column.from_float_mv(
                dst,
                name=f"{self}, {col.name}",
                type=col._type
            )
        # -------------- end of epilogue ---------------

    cdef void eval(self, unsigned l, double* dst, const double* src):
        self.delegate.eval(l, dst, src)
        for i in range(l):
            dst[i] = sqrt(dst[i])

