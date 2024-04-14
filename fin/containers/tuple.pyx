from cpython.ref cimport Py_XDECREF

from fin.mathx cimport balloc

# ======================================================================
# Custom Tuple
# ======================================================================
cdef class Tuple:
    """ A Tuple implementation with mostly Cython interface.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("You must use a factory method to create a Tuple")

    def __len__(self):
        return self._size

    def __del__(self):
        tuple_dealloc(self)

    def __getitem__(self, idx):
        cdef PyObject *obj = tuple_get_item(self, idx)
        if obj is NULL:
            return None

        return <object>obj

    def __setitem__(self, idx, obj):
        tuple_set_item(self, idx, <PyObject*>obj)

    @staticmethod
    def create(size, sequence):
        return tuple_create(size, sequence)

    def new_view(self, start, end):
        if start < 0:
            start += self._size
        if end < 0:
            end += self._size

        # tuple_new_view will take care of additional tests
        return tuple_new_view(self, start, end)

cdef Tuple tuple_alloc(unsigned size):
    cdef Tuple result = Tuple.__new__(Tuple)
    result._size = size
    result._buffer = balloc(size*sizeof(PyObject*))
    result._base_ptr = <PyObject**>result._buffer.data.as_chars

    return result

cdef int tuple_dealloc(Tuple self) except -1:
    cdef unsigned   i
    cdef PyObject*  tmp

    for i in range(self._size):
        if self._base_ptr[i] != NULL:
            tmp = self._base_ptr[i]
            self._base_ptr[i] = NULL
            Py_XDECREF(tmp)

    self._buffer = None
    self._base_ptr = NULL

cdef Tuple tuple_create(unsigned size, object sequence):
    cdef Tuple      result = tuple_alloc(size)
    cdef PyObject*  obj
    cdef unsigned   idx = 0

    for item in sequence:
        if idx == size:
            raise ValueError(f"Initialization eqeunce too long")

        obj = <PyObject*>item
        Py_XINCREF(obj)
        result._base_ptr[idx] = obj

        idx += 1

    return result

cdef Tuple tuple_new_view(Tuple self, unsigned start, unsigned end):
    """ Create a new Tuple instance sharing the underlying buffer,
        but exposing only the items in the range [start;end).

        This is a zero-copy operation.
    """
    if not start <= end <= self._size:
        raise ValueError(f"Indices out of range ({start}, {end})")

    cdef Tuple result = Tuple.__new__(Tuple)
    result._size = end-start
    result._buffer = self._buffer
    result._base_ptr = self._base_ptr+start

    return result


