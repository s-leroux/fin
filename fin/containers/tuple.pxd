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

cdef Tuple tuple_create(unsigned size, object sequence)
cdef int tuple_dealloc(Tuple self) except -1

cdef Tuple tuple_new_view(Tuple self, unsigned start, unsigned end)

cdef inline PyObject *tuple_get_item(Tuple self, unsigned idx) except? NULL:
    if idx >= self._size:
        raise IndexError(f"Tuple index {idx} out of range")

    return self._base_ptr[idx]

