from cpython.ref cimport Py_XDECREF, Py_INCREF
from libc.string cimport memset

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

    @staticmethod
    def from_sequence(sequence):
        return tuple_from_sequence(sequence)

    @staticmethod
    def from_constant(size, c):
        return tuple_from_constant(size, c)

    def new_view(self, start, end):
        if start < 0:
            start += self._size
        if end < 0:
            end += self._size

        # tuple_new_view will take care of additional tests
        return tuple_new_view(self, start, end)

    def remap(self, mapping):
        cdef array.array arr = array.array("i", mapping)
        # Above: use a *signed* int array to accomodate for the -1u
        # magic value ("MISSING" constant).

        return tuple_remap(self, len(mapping), arr.data.as_uints)

    # ------------------------------------------------------------------
    # For testing purposes ONLY
    # ------------------------------------------------------------------
    def tst_resize(self, new_size):
        tuple_resize(self, new_size)

# ======================================================================
# Memory allocation
# ======================================================================
cdef Tuple tuple_alloc(unsigned size):
    cdef Tuple result = Tuple.__new__(Tuple)
    result._size = size
    result._buffer = balloc(size*sizeof(PyObject*))
    result._base_ptr = <PyObject**>result._buffer.data.as_chars

    return result

cdef inline int tuple_resize(Tuple self, unsigned new_size) except -1:
    if new_size < self._size:
        tuple_shrink(self, new_size)
    elif new_size > self._size:
        tuple_grow(self, new_size)
    else:
        pass # do nothing

cdef inline int tuple_grow(Tuple self, unsigned new_size) except -1:
    array.resize_smart(self._buffer, new_size*sizeof(PyObject*))
    self._base_ptr = <PyObject**>self._buffer.data.as_chars
    memset(self._base_ptr+self._size, 0, (new_size-self._size)*sizeof(PyObject*))
    self._size = new_size

cdef inline int tuple_shrink(Tuple self, unsigned new_size):
    cdef unsigned i
    cdef PyObject *tmp

    for i in range(new_size, self._size):
        tmp = self._base_ptr[i]
        self._base_ptr[i] = NULL
        Py_XDECREF(tmp)

    array.resize_smart(self._buffer, new_size*sizeof(PyObject*))
    self._base_ptr = <PyObject**>self._buffer.data.as_chars
    self._size = new_size

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

# ======================================================================
# Factory methods
# ======================================================================
cdef Tuple tuple_create(unsigned size, object sequence):
    cdef Tuple      result = tuple_alloc(size)
    cdef PyObject*  obj
    cdef unsigned   idx = 0

    for item in sequence:
        if idx == size:
            raise ValueError(f"Initialization sequence too long")

        obj = <PyObject*>item
        Py_XINCREF(obj)
        result._base_ptr[idx] = obj

        idx += 1

    return result

cdef Tuple tuple_from_sequence(object sequence):
    cdef unsigned   size = 10 # Guess...
    cdef Tuple      result = tuple_alloc(size)

    cdef unsigned i = 0
    for item in sequence:
        if i == size:
            # Same strategy than for CPython tuple:
            # https://github.com/python/cpython/blob/e01831760e3c7cb9cdba78b048c8052808a3a663/Objects/abstract.c#L2090
            size += 10
            size += size >> 2
            tuple_resize(result, size)

        result._base_ptr[i] = <PyObject*>item
        Py_INCREF(item)

        i += 1

    # adjust to the correct size:
    tuple_resize(result, i)

    return result

cdef Tuple tuple_from_constant(unsigned size, object c):
    cdef Tuple      result = tuple_alloc(size)

    cdef unsigned i
    for i in range(size):
        result._base_ptr[i] = <PyObject*>c
        Py_INCREF(c)

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

cdef Tuple tuple_remap(Tuple self, unsigned count, unsigned* mapping):
    """ Create a new Tuple instance with the items reordered according to `mapping`.

        The special value `<unsigned>-1` in the mapping insert `None` in the tuple.
    """
    cdef Tuple      result = tuple_alloc(count)
    cdef unsigned   idx
    cdef unsigned   src
    cdef unsigned   MISSING = -1
    cdef PyObject   *obj

    for idx in range(count):
        src = mapping[idx]
        if src == MISSING:
            obj = <PyObject*>None
        elif src >= self._size:
            raise ValueError(f"Remapping index out of range (src)")
        else:
            obj = self._base_ptr[src]

        Py_XINCREF(obj)
        result._base_ptr[idx] = obj

    return result