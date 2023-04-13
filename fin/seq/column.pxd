from cpython cimport array
from fin.mathx cimport NaN

import array

# ======================================================================
# Utilities
# ======================================================================
cpdef FColumn as_fcolumn(sequence)

# ======================================================================
# Column class
# ======================================================================
cdef class AnyColumn:
    pass

cdef class FColumn(AnyColumn):
    """
    A Fast float column.

    This is an intermediate representation of a column used to speedup calculations.
    """
    cdef readonly double[::1]    values
    cdef readonly str name

