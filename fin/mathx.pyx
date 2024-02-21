from cpython cimport array
from libc.math cimport erf, sqrt

from fin.mathx cimport NaN

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN = float("NaN")

# ======================================================================
# Statistical functions
# ======================================================================
cpdef cdf(double x, double mu=0.0, double sigma=1.0):
    """ Cumulative distribution function for x normal distributions.
    """
    x = (x-mu)/sigma
    return (1.0 + erf(x / sqrt(2.0))) / 2.0


# ======================================================================
# Array management
# ======================================================================
cdef array.array double_array_template = array.array('d', [])

cdef inline double[::1] alloc(unsigned n, double init_value = NaN):
    """
    Allocate a contiguous array of n double initialized to NaN.
    Return a view on the array.
    """
    cdef double[::1] arr = array.clone(double_array_template, n, zero=False)[::1]
    cdef unsigned i
    for i in range(n):
        arr[i] = init_value

    return arr


cdef inline array.array aalloc(unsigned n, double init_value = NaN):
    """
    Allocate a contiguous array of n double initialized to NaN.
    Return the array.
    """
    cdef array.array arr = array.clone(double_array_template, n, zero=False)
    cdef unsigned i
    for i in range(n):
        arr.data.as_doubles[i] = init_value

    return arr

