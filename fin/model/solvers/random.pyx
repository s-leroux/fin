# cython: cdivision=True

from fin.model.solvers.solver cimport Domain, Eq, Solver

from cpython cimport array

from fin.mathx cimport aalloc, vrand
from fin cimport tuplex

cdef inline void _populate(unsigned count, unsigned n, double* points, const Domain* domains):
    vrand(count*n, points)
    cdef double *it = points
    cdef unsigned i
    cdef unsigned j
    for i in range(count):
        for j in range(n):
            if domains[j]._max == domains[j]._min:
                it[0] = domains[j]._max
            else:
                it[0] *= domains[j]._max - domains[j]._min
                it[0] += domains[j]._min
            it += 1

cdef inline _evaluate(
        unsigned k, const Eq *eqs,
        unsigned count, unsigned n, double* points
        ):
    cdef unsigned i
    cdef unsigned j
    cdef unsigned h
    cdef double* curr_point = points
    cdef double* best_solution = NULL
    cdef double  best_score = 1./0.
    cdef double score, tmp
    for i in range(count):
        score = 0.0
        point = tuplex.from_doubles(n, curr_point)
        for j in range(k):
            # map params to a list
            # XXX We might use the PyTuple low-level API here
            params = [ point[eqs[j].params[h]] for h in range(eqs[j].count) ]
            tmp = (<object>eqs[j].fct)(*params)
            score += tmp*tmp

        if score < best_score:
            best_score = score
            best_solution = curr_point

        curr_point += n

    return (
        best_score,
        tuplex.from_doubles(n, best_solution),
            )

# ======================================================================
# Random solver
# ======================================================================
cdef class RandomSolver(Solver):
    """ Pick points in the search space at random. Return the best guess.
    """
    cdef unsigned _count

    def __cinit__(self, count):
        self._count = count

    cdef c_solve(self, unsigned n, Domain* domains, unsigned k, Eq *eqs):
        # Create a buffer large enough to store `count` points
        cdef unsigned buffer_size = self._count*n
        cdef array.array points = aalloc(buffer_size)
        cdef double *points_base_ptr = points.data.as_doubles

        _populate(self._count, n, points_base_ptr, domains)
        return _evaluate(k, eqs, self._count, n, points_base_ptr,)


