from cpython.ref cimport PyObject

# ======================================================================
# Structs
# ======================================================================
cdef struct Domain:
    double _min # XXX Those are public fields. Remove the leading underscore
    double _max

cdef struct Eq:
    PyObject    *fct
    unsigned    count
    int         *params

# ======================================================================
# Base class for Cython solvers
# ======================================================================
cdef class Solver:
    cdef c_solve(self, unsigned n, Domain* domains, unsigned k, Eq *eqs)

