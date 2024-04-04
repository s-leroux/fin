from cpython cimport array
from fin.mathx cimport aalloc, ialloc, balloc

# ======================================================================
# Solver
# ======================================================================
cdef class Solver:
    """ Base class for Cython solvers.
    """

    cdef c_solve(self, unsigned n, Domain* domains, unsigned k, Eq *eqs):
        cdef unsigned i, j
        for i in range(n):
            print(f"{domains[i]._min} {domains[i]._max}")

        for i in range(k):
            print(<object>(eqs[i].fct))
            for j in range(eqs[i].count):
                    print(eqs[i].params[j])

    def solve(self, domains, eqs):
        # Convert the domains list to a C structure
        cdef unsigned n = len(domains)
        cdef array.array    domain_buffer = aalloc(len(domains)*2)
        cdef Domain  *domains_array = <Domain*>domain_buffer.data.as_doubles
        cdef Domain *ptr = domains_array

        for a, b in domains:
            ptr._min = a
            ptr._max = b
            ptr += 1

        # Reserve a buffer to store function parameter indices
        cdef pcount = 0
        for fct, params in eqs:
            pcount += len(params)
        cdef array.array params_buffer = ialloc(pcount)
        cdef int     *params_array = params_buffer.data.as_ints
        cdef int     *params_ptr = params_array

        # Convert the eqs list to a C structure
        cdef unsigned k = len(eqs)
        cdef array.array eqs_buffer = balloc(k*sizeof(Eq))
        cdef Eq     *eqs_array = <Eq*>eqs_buffer.data.as_chars
        cdef Eq     *eq_ptr = eqs_array
        cdef unsigned i
        cdef unsigned j
        for fct, params in eqs:
            eq_ptr.fct = <PyObject*>fct
            eq_ptr.count = len(params)
            eq_ptr.params = params_ptr
            for param in params:
                params_ptr[0] = param
                params_ptr += 1
            eq_ptr += 1

        return self.c_solve(n, domains_array, k, eqs_array)
