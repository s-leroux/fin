# cython: boundscheck=False
# cython: cdivision=True

from fin.seq.ag.corex cimport CAggregateFunction
from fin.seq.column cimport Column

cdef class _MaximumDrawdown(CAggregateFunction):
    cdef eval(self, Column col, unsigned begin, unsigned end):
        if begin == end:
            return 0.0/0.0

        cdef const double* src = col.as_float_values()
        cdef unsigned i = begin
        cdef double maximum = src[i]

        i+=1
        while i < end:
            if src[i] > maximum:
                maximum = src[i]

            i+= 1

        return maximum-src[i-1]

maximum_drawdown = _MaximumDrawdown()
