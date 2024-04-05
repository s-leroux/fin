from cpython.tuple cimport PyTuple_New

cdef extern from "Python.h":
    PyObject* PyFloat_FromDouble(double v)
    # Above:
    # Do NOT use the definition from `cpython.float` to avoid
    # automatic DECREF calls.

# ======================================================================
# Tuple utility API
# ======================================================================
cdef tuple from_doubles(unsigned n, const double* buffer):
    """ Create a tuple from an array of floats.
    """
    cdef tuple t = PyTuple_New(n)
    cdef PyObject** items = (<PyTupleObject*>t).ob_item
    cdef unsigned i
    for i in range(n):
        items[i] = PyFloat_FromDouble(buffer[i])
        if not items[i]:
            raise MemoryError()

    return t

