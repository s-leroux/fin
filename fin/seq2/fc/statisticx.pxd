from fin.seq2 cimport column
from fin.seq2.fc cimport functorx

# ======================================================================
# Math and stats
# ======================================================================
cdef class var(functorx.Functor1):
    """
    Compute the Variance over a n-period window.
    """
    cdef double a
    cdef double b
    cdef unsigned n
    cdef double correction

    cdef init(self, unsigned n, double correction)
    cdef make_name(self, col)
    cdef void eval(self, unsigned l, double* dst, const double* src)

cdef class stdev(functorx.Functor1):
    """
    Compute the Standard Deviation over a n-period window.
    """
    cdef var delegate

    cdef init(self, unsigned n, var v)
    cdef make_name(self, col)
    cdef void eval(self, unsigned l, double* dst, const double* src)

