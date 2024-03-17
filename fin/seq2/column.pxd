from cpython cimport array
import array

# ======================================================================
# Utilities
# ======================================================================
cpdef Column as_column(sequence)

# ======================================================================
# Column class
# ======================================================================
cdef class Column:
    """
    A column.
    """
    cdef tuple          _py_values
    cdef array.array    _f_values

    cdef tuple          get_py_values(self)
    cdef array.array    get_f_values(self)

    cdef Column         c_remap(self, unsigned len, const unsigned* mapping)
