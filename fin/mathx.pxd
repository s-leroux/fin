from cpython cimport array

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN

cpdef cdf(double x, double mu=*, double sigma=*)

cdef double[::1] alloc(unsigned n, double init_value=*)
cdef array.array aalloc(unsigned n, double init_value=*)

from libc.math cimport isnan

