from cpython.ref cimport PyObject
from cpython.ref cimport Py_XINCREF, Py_XDECREF

from cpython cimport array

# ======================================================================
# Custom Tuple
# ======================================================================
cdef class Tuple:
    """ A Tuple implementation with mostly Cython interface.
    """
    cdef unsigned        _size       # Size in items
    cdef array.array     _buffer
    cdef PyObject        **_base_ptr

    @staticmethod
    cdef Tuple create(unsigned size, object sequence)

    @staticmethod
    cdef Tuple from_sequence(object sequence)

    @staticmethod
    cdef Tuple from_constant(unsigned size, object sequence)
    
    cdef Tuple new_view(self, int start, int end)

    cdef Tuple remap(self, unsigned count, unsigned* mapping)

cdef inline PyObject *tuple_get_item(Tuple self, unsigned idx) except? NULL:
    if idx >= self._size:
        raise IndexError(f"Tuple index {idx} out of range")

    return self._base_ptr[idx]

