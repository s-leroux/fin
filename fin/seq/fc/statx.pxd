from fin.seq cimport column
from fin.seq.fc cimport funcx

# ======================================================================
# Math and stats
# ======================================================================
cdef class var(funcx.Functor1):
    """
    Compute the Variance over a n-period window.
    """
    cdef double a
    cdef double b
    cdef unsigned n
    cdef double correction

    cdef init(self, unsigned n, double correction)
    cdef make_name(self, col)
    cdef void eval(self, unsigned l, funcx.param_t* dst, const funcx.param_t* src)

cdef class stdev(funcx.Functor1):
    """
    Compute the Standard Deviation over a n-period window.
    """
    cdef var delegate

    cdef init(self, unsigned n, var v)
    cdef make_name(self, col)
    cdef void eval(self, unsigned l, funcx.param_t* dst, const funcx.param_t* src)

