# cython: boundscheck=False
# cython: cdivision=True

from fin.seq.ag.corex cimport CAggregateFunction
from fin.seq.column cimport Column
from fin.mathx cimport isnan

cdef class _Drawdown(CAggregateFunction):
    """ Calculate the actual drawdown over a range of values.

        The drawdown is defined as :
            \max_{t-n < i <= t}(V_i)-V_t
    """

    cdef eval(self, Column col, unsigned begin, unsigned end):
        if begin == end:
            return 0.0

        cdef const double* src = col.as_float_values()
        cdef unsigned i = begin
        cdef double maximum = src[i]
        cdef double guard = src[i] # Used to check for NaN values

        i+=1
        while i < end:
            guard += src[i]
            if src[i] > maximum:
                maximum = src[i]

            i+= 1
        
        if isnan(guard):
            return None

        return maximum-src[i-1]

cdef class _MaximumDrawdown(CAggregateFunction):
    """ Calculate the maximum drawdown over a range of values.

        The maximum drawdown is defined as the maximum possible loss over the range.
    """

    cdef eval(self, Column col, unsigned begin, unsigned end):
        if begin == end:
            return 0.0

        cdef const double* src = col.as_float_values()
        cdef unsigned i = begin
        cdef double maximum = src[i]
        cdef double drawdown = 0.0
        cdef double guard = src[i] # Used to check for NaN values

        i+=1
        while i < end:
            guard += src[i]
            if src[i] > maximum:
                maximum = src[i]
            else:
                if maximum-src[i] > drawdown:
                    drawdown = maximum-src[i]

            i+= 1

        if isnan(guard):
            return None
        
        return drawdown

drawdown = _Drawdown()
maximum_drawdown = _MaximumDrawdown()
