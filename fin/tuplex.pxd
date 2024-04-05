from cpython.ref cimport PyObject

cdef extern from "Python.h":
    ctypedef struct PyTupleObject:
        PyObject *ob_item[1]

# ======================================================================
# Tuple utility API
# ======================================================================
cdef tuple from_doubles(unsigned n, const double* buffer)

