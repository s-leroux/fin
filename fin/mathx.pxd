from cpython cimport array

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN
from libc.math cimport isnan

cpdef double cdf(double x, double mu=*, double sigma=*)


# ======================================================================
# Memory allocation
# ======================================================================
cdef double[::1] alloc(unsigned n, double init_value=*)
cdef array.array aalloc(unsigned n, double init_value=*)
cdef array.array ialloc(unsigned n, int init_value=*)
cdef array.array ualloc(unsigned n, unsigned init_value=*)
cdef array.array balloc(unsigned n, char init_value=*)


# ======================================================================
# Vectorized operations
# ======================================================================
cdef void vrand(unsigned n, double* buffer)
