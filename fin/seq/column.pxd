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
    cdef Tuple          _py_values # Python objects
    cdef array.array    _f_values  # Array of doubles
    cdef array.array    _t_values  # Array of ternary values (-1, 0, +1)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    cdef unsigned       length
    cdef unsigned       _id
    cdef str            _name
    cdef object         _type

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------
    cdef Tuple          get_py_values(self)
    cdef array.array    get_f_values(self)
    cdef array.array    get_t_values(self)

    cdef const double*  as_float_values(self) except NULL
    cdef const signed char*  as_ternary_values(self) except NULL
    # Methods `as_....()` above:
    # The returned buffer is valid as long as the column exists.
    # Raise an exception if the column's values cannot be represented using the
    # requested type.


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

