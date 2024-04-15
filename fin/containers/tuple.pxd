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
    
    @staticmethod
    cdef Tuple combine(Tuple ta, Tuple tb,
            unsigned n, const unsigned *mappingA, const unsigned *mappingB)

    cdef object get_item(self, Py_ssize_t idx)
    cdef Tuple slice(self, Py_ssize_t start, Py_ssize_t stop)

    cdef Tuple remap(self, unsigned count, const unsigned* mapping)

    cdef Tuple shift(self, int offset)

cdef inline PyObject *tuple_get_item(Tuple self, Py_ssize_t idx) except? NULL:
    if idx < 0:
        idx += self._size

    if not 0 <= idx < self._size:
        raise IndexError(f"Tuple index {idx} out of range")

    return self._base_ptr[idx]

