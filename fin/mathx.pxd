from cpython cimport array

# ======================================================================
# Math utilities for Cython
# ======================================================================
cdef double NaN

cdef double[::1] alloc(unsigned n, double init_value=*)

from libc.math cimport isnan

