from cpython cimport array

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN

cdef double[::1] alloc(unsigned n)

from libc.math cimport isnan

