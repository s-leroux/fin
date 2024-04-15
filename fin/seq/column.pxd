from cpython cimport array
from fin.containers.tuple cimport Tuple
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
    # ------------------------------------------------------------------
    # Polymorphic representation of the values:
    # ------------------------------------------------------------------
    cdef Tuple          _py_values
    cdef array.array    _f_values

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    cdef unsigned       _id
    cdef str            _name
    cdef object         _type

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    cdef Tuple          get_py_values(self)
    cdef array.array    get_f_values(self)

    cdef str            get_name(self)
    cdef object         get_type(self)

    # ------------------------------------------------------------------
    # Cython-specific interface
    # ------------------------------------------------------------------
    cdef Column         c_remap(self, unsigned len, const unsigned* mapping)
    cdef Column         c_rename(self, str newName)
    cdef Column         c_shift(self, int n)

    cdef Column         c_add_scalar(self, double scalar)
    cdef Column         c_sub_scalar(self, double scalar)
    cdef Column         c_mul_scalar(self, double scalar)
    cdef Column         c_div_scalar(self, double scalar)
