from cpython cimport array
import array

# ======================================================================
# Utilities
# ======================================================================
cpdef str get_column_name(obj)
cpdef Column as_column(sequence, name=*)

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

cdef class Column:
    """
    A column.
    """
    cdef str            _name
    cdef tuple          _py_values
    cdef array.array    _f_values

    cdef tuple          get_py_values(self)
    cdef array.array    get_f_values(self)
