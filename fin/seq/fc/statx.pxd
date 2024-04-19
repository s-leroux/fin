from fin.seq cimport column

# ======================================================================
# Math and stats
# ======================================================================
cdef class var:
    """
    Compute the Variance over a n-period window.
    """
    cdef double a
    cdef double b
    cdef unsigned n
    cdef double correction

    cdef init(self, unsigned n, double correction)
    cdef void eval(self, unsigned l, double* dst, const double* src)

cdef class stdev:
    """
    Compute the Standard Deviation over a n-period window.
    """
    cdef var delegate

    cdef init(self, unsigned n, var v)
    cdef void eval(self, unsigned l, double* dst, const double* src)

