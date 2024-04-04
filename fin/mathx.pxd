from cpython cimport array

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN

cpdef double cdf(double x, double mu=*, double sigma=*)

cdef double[::1] alloc(unsigned n, double init_value=*)
cdef array.array aalloc(unsigned n, double init_value=*)
cdef array.array ialloc(unsigned n, int init_value=*)
cdef array.array balloc(unsigned n, char init_value=*)

from libc.math cimport isnan

